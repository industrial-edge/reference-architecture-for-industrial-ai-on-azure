<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# Secrets Store - Azure Key Vault best practices

  The solution uses Azure Key Vault as a secure location for storing secrets and making them available as required to various parts of the project.
  This approach prevents "secrets sprawl" (when an organisation stores secrets in many different places without access control, audit, logging, or even encryption)
  and ensures best practices are followed:
   * no secrets are stored in source control
   * having a central place for storing secrets, keys or certificates (all sensitive pieces of configuration are kept in a secure place in a managed way)
   * automatic encryption when stored and decryption when used by an authorised applications
   * audit and logging (who accessed the secret and when)

   Best practices implemented:
   - a separate Key Vault is deployed and used per environment (granular isolation reduces the threat if there is a breach)
   - soft-delete is enabled (to guard againsts malicious or accidental deletion of the Key Vault objects (secrets, certificates, keys) and the Key Vault itself)
   - logging is enabled

   The Key Vault is deployed as part of the shared module and any new properties and resources needed for enabling soft delete and logging are part of its main.tf file.

   ```text
infrastructure
|__ shared
        |__ main.tf
          * Key Vault
          * Storage Account
          * Azure Monitor Diagnostic Settings
          * Storage Management Policy
        |__ variables.tf
          * kv_soft_delete_retention_days
          * storage_mngmnt_policy_kv_logs_delete_after
```

## Key Vault logging
When logging is enabled for Key Vault information of who and when accessed what is logged:
- all unautheticated requests (requests that resulted in a 401 unauthorised, for example because the bearer token is missing, invalid, malformed, expired)
- all authenticated requests (including bad requests)
- operations on Key Vault itself (i.e creation, deletion, setting access policies)
- operations on Key Vault objects (secrets, keys, certificates) (i.e creating, modifying, deleting, getting and listing)  

Key Vault logging is enabled through the Azure Monitor Diagnosting Settings resource, which takes the ID of the existing Key Vault and the ID of the new storage account
in which the logs are to be stored.

```text
resource "azurerm_monitor_diagnostic_setting" "main" {
  target_resource_id = azurerm_key_vault.kv.id
  storage_account_id = azurerm_storage_account.main.id
  ...
```

Once the diagnostic settings is in place the logs are stored in the ```insights-logs-auditevent``` container of the storage account inside blobs.
The names of the blobs are in the following format: ```resourceId=<ARM resource ID>/y=<year>/m=<month>/d=<day of month>/h=<hour>/m=<minute>/filename.json.```

It is good practice to set a retention policy for the logs, so that older logs are automatically deleted after a specified amount of time. This is achived
through the Lifecycle Management feature of the storage account, basically by creating a resource of type ```azurerm_storage_management_policy``` for the storage acccount.
This is configurable through the ```storage_mngmnt_policy_kv_logs_delete_after``` variable.

## Key Vault soft delete
 Soft delete is enabled for key vault in order to prevent accidental deletion of key vault and secrets, certificates and keys stored inside key vault.
 When a key vault or a key vault object is deleted it remains recoverable for a configurable retention period: the variable used to configure the retention period is ```kv_soft_delete_retention_days``` and the property on the ```azurerm_key_vault``` resource is ```soft_delete_retention_days```. Once this is set, soft delete is enabled for key vault.

In the Azure Portal, this is visible in Properties under the Settings menu: Setting => Properties => Soft Delete = Soft delete has been enabled for this Key Vault

Example recovering a secret from a soft delete state using az cli
* View the Key Vault secrets:  ```az keyvault secret list --vault-name <key_vault_name>```
* View the Key Vault secrets in the soft delete state: ```az keyvault secret list-deleted --vault-name <key_vault_name>```
* Choose secret not in soft delete state for deletion: ```az keyvault secret delete --name <secret_name> --vault-name <key-vault-name>```
* Observe secret now in soft delete state: ```az keyvault secret list-deleted --vault-name <key_vault_name>``` and no longer amongsts the key vault secrets list ```az keyvault secret list --vault-name <key_vault_name>```
* Recover the secret from the soft delete state: ```az keyvault secret recover --name <secret_name> --vault-name <key_vault_name> ```
and observe secret no longer in soft delete state

In the Portal, the secrets in soft delete state can be viewed and managed under ```Manage Deleted Secrets``` (Objects => Secrets => Manage Deleted Secrets) (similarly for keys Objects= > Keys => Manage Deleted Keys and certificate Objects => Certificates => Manage Deleted Certificates)

Example deleting a KV and then recovering it using az cli:
* Deleting the Key Vault: ```az keyvault delete --subscription <subacription_id> -g <resource_group_name> -n <key_vault_name>```
* Recovering the KV: ```az keyvault recover --subscription <subscription_id> -n <key_vault_name>`s``

In the Portal this is managed under Key Vaults => Managed Deleted Vaults
