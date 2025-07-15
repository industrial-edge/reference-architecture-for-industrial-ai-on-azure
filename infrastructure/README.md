<!--
SPDX-FileCopyrightText: 2025 Siemens AG

SPDX-License-Identifier: MIT
-->

## Requirements

* Terraform version: >= 0.13
* Golang env: >= 1.19
* Terraform-docs: https://github.com/terraform-docs/terraform-docs
* Terratest: https://terratest.gruntwork.io/

## Generating documentation

To generate the Terraform module documentation, go to the module directory and enter this command:

```sh
terraform-docs markdown table --output-file README.md --output-mode inject .
```

Then, the documentation will be generated inside the component root directory.

## Creating a Test

Create a new GO file under the test directory called `end2end_test.go`.
Use the following command to init the module: `go mod init test`. This will generate a .mod file.
Execute the command `go mod tidy` to generate the `go.sum` file which contains the cryptographic checksums of the module's dependencies.

## Executing the Terraform Tests

The tests in this project are made using `Terratest`. Go to the `test` directory. But before building the tests, you need to add any missing module requirements necessary to build the current module’s packages and dependencies, using the command:

```sh
$ go mod tidy
```

After executing this command, we can run the tests using the command:

```sh
$ go test -timeout 30m end2end_test.go
```

> The `-timeout 30m` paramter will define the timeout to 30 minutes instead of the default of 10 minutes.

## Testing the Terraform Configuration on Local Machine

To execute the Terraform configuration you first need to make sure that you're using the right Azure subscription by running the commands:

```sh
az login
az account show
```

If the correct subscription id is displayed, you're all set. If not, you have to manually set the subscription by running:

```sh
az account set --subscription <SUBSCRIPTION_ID>
```

You can test individual modules by running the terraform commands inside each module folder. If you want to store the Terraform state in the Storage Account deployed in Azure you need to add the following information in the corresponding `module/backend.tf` file:
```
    # resource_group_name  = ""
    # storage_account_name = ""
    # container_name       = ""
    # key                  = "terraform.tfstate"
```
You can find this information in the Azure Portal, navigating to the resource group responsible for storing the Terraform state.
For testing purposes you can skip storing the Terraform state in Azure by commenting out the content of the `backend.tf` file.

Execute the Terraform configuration by running the following commands inside the module directory:

```sh
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
```
