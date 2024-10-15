package test

import (
	"fmt"
	"os"
	"strings"
	"testing"

	"github.com/gruntwork-io/terratest/modules/azure"
	"github.com/gruntwork-io/terratest/modules/terraform"
	test_structure "github.com/gruntwork-io/terratest/modules/test-structure"
	"github.com/stretchr/testify/assert"
)

type ServicePrincipalIds struct {
	mainServicePrincipalId string
}

type Permissions struct {
	key         string
	secret      string
	certificate string
	storage     string
}

func performKeyVaultPermissionsAssertions(t *testing.T, actual Permissions, expected map[string]string) {
	assert.Equal(t, expected["key"], actual.key, "KeyPermission mismatch")
	assert.Equal(t, expected["secret"], actual.secret, "SecretPermissions mismatch")
	assert.Equal(t, expected["certificate"], actual.certificate, "CertificatePermissions mismatch")
	assert.Equal(t, expected["storage"], actual.storage, "StoragePermissions mismatch")
}

func assertKeyVaultProperties(t *testing.T, resourceGroupName string, keyVaultName string, principalIds ServicePrincipalIds) {

	var actualMainServicePrincipalPermissions Permissions

	expectedMainServicePrincipalPermissions := map[string]string{
		"key":         "&[Create Get List Recover Purge]",
		"secret":      "&[Set Get Delete Purge Recover List]",
		"certificate": "&[Create List Get Purge Recover]",
		"storage":     "&[Get]",
	}

	keyVaultInstance := azure.GetKeyVault(t, resourceGroupName, keyVaultName, "")
	assert.NotEmpty(t, keyVaultInstance, "KeyVault is not created")
	assert.NotEmpty(t, *keyVaultInstance.Properties.AccessPolicies, "AccessPolicies list must contain roles")

	policies := *keyVaultInstance.Properties.AccessPolicies

	for _, policy := range policies {
		if *policy.ObjectID == principalIds.mainServicePrincipalId {
			actualMainServicePrincipalPermissions = Permissions{
				key:         fmt.Sprintf("%+v", policy.Permissions.Keys),
				secret:      fmt.Sprintf("%+v", policy.Permissions.Secrets),
				certificate: fmt.Sprintf("%+v", policy.Permissions.Certificates),
				storage:     fmt.Sprintf("%+v", policy.Permissions.Storage),
			}
		}
	}

	// Assert permissions for the main service principal
	performKeyVaultPermissionsAssertions(t, actualMainServicePrincipalPermissions, expectedMainServicePrincipalPermissions)
}

func assertKeyVaultSecrets(t *testing.T, keyVaultName string, resourceSuffix string) {
	assert.True(t, azure.KeyVaultSecretExists(t, keyVaultName, "ml-container-registry-name-"+resourceSuffix))
	assert.True(t, azure.KeyVaultSecretExists(t, keyVaultName, "AppInsights-ConnectionString-"+resourceSuffix))
	assert.True(t, azure.KeyVaultSecretExists(t, keyVaultName, "AppInsights-ApplicationId-"+resourceSuffix))
	assert.True(t, azure.KeyVaultSecretExists(t, keyVaultName, "KeyVault-Suffix"))
	assert.True(t, azure.KeyVaultSecretExists(t, keyVaultName, "iotmngmt-iothub-primary-connection-string-"+resourceSuffix))
	assert.True(t, azure.KeyVaultSecretExists(t, keyVaultName, "iotmngmt-iothub-eventhubendpoint-"+resourceSuffix))
	assert.True(t, azure.KeyVaultSecretExists(t, keyVaultName, "iotmngmt-iothub-name-"+resourceSuffix))
	assert.True(t, azure.KeyVaultSecretExists(t, keyVaultName, "iotmngmt-iothub-eventhub-compatible-endpoint-"+resourceSuffix))
}

func assertContainerRegistryProperties(t *testing.T, resourceGroupName string, containerRegistryName string) {
	assert.True(t, azure.ContainerRegistryExists(t, containerRegistryName, resourceGroupName, ""))

	containerRegistryInstance := azure.GetContainerRegistry(t, containerRegistryName, resourceGroupName, "")
	assert.True(t, *containerRegistryInstance.AdminUserEnabled)
}

func TestEndToEndOutputs(t *testing.T) {
	t.Parallel()

	//value of variable represents the directory that contains the Terraform configuration to deploy
	fixtureFolder := "../example"

	//the teardown stage: this stage is responsible for cleaning up the infrastructure.
	defer test_structure.RunTestStage(t, "teardown", func() {
		//this Terratest function allows to load Terraform options (config, variables etc.) from the state
		terraformOptions := test_structure.LoadTerraformOptions(t, fixtureFolder)

		terraform.Destroy(t, terraformOptions)
	})

	//the setup stage: this stage is responsible for running Terraform to deploy the configuration
	test_structure.RunTestStage(t, "setup", func() {
		terraformOptions := &terraform.Options{
			TerraformDir:    fixtureFolder,
			TerraformBinary: "tofu",
			BackendConfig: map[string]interface{}{
				"resource_group_name":  os.Getenv("TF_VAR_resource_group_name"),
				"storage_account_name": os.Getenv("TF_VAR_storage_account_name"),
				"container_name":       os.Getenv("TF_VAR_container_name"),
			},
		}

		// Save options for later test stages
		//this Terraform function allows to save Terraform options (config, variables etc.) to the state
		test_structure.SaveTerraformOptions(t, fixtureFolder, terraformOptions)

		terraform.InitAndApply(t, terraformOptions)
	})

	//the validate stage: this stage is responsible for doing the validation checks/assertions
	test_structure.RunTestStage(t, "validate", func() {

		terraformOptions := test_structure.LoadTerraformOptions(t, fixtureFolder)

		resourceGroupName := terraform.Output(t, terraformOptions, "resource_group_name")
		keyVaultName := terraform.Output(t, terraformOptions, "key_vault_name")
		containerRegistryName := terraform.Output(t, terraformOptions, "container_registry_name")
		resourceSuffix := terraform.Output(t, terraformOptions, "resource_suffix")
		mainServicePrincipalId := terraform.Output(t, terraformOptions, "main_service_principal_id")

		servicePrincipalIds := ServicePrincipalIds{
			mainServicePrincipalId: mainServicePrincipalId,
		}

		assert.True(t, strings.Contains(resourceGroupName, "test"))

		assertKeyVaultProperties(t, resourceGroupName, keyVaultName, servicePrincipalIds)
		assertKeyVaultSecrets(t, keyVaultName, resourceSuffix)
		assertContainerRegistryProperties(t, resourceGroupName, containerRegistryName)

	})
}
