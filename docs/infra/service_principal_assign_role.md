<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

### 1. Prerequisites
To assign roles, the account used must have Microsoft.Authorization/roleAssignments/write permissions, such as User Access Administrator or Owner

### Steps to assign the Storage Blob Data Contributor to the service principal
1. Identify the unique id of the object
For an Azure AD service principal (identity used by an application), you need the service principal object ID. To get the object ID, you can use az ad sp list. For a service principal, use the object ID and not the application ID.

```sh
az ad sp list --all --query "[].{displayName:displayName, id:id}" --output tsv
az ad sp list --display-name "{displayName}"
```

Assign the "Storage Blob Data Reader" role to the service principal with object ID <OBJECT_ID> for all blob containers at a resource group scope
```sh
az role assignment create --assignee "{service_principal_object_id}" \
--role "Storage Blob Data Reader" \
--scope "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
```

Assign "Storage Blob Data Contributor" role for all blob containers at a resource group scope

```sh
az role assignment create --assignee "{service_principal_object_id}" \
--role "Storage Blob Data Contributor" \
--scope "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
```
or if even more granular permissions are required
Assign "Storage Blob Data Contributor" role for all blob containers in a storage account resource scope

```sh
az role assignment create --assignee "{service_principal_object_id}" \
--role "Storage Blob Data Contributor" \
--scope "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Storage/storageAccounts/{storage_account}"
```

### Side note:
If you create a new service principal and immediately try to assign a role to that service principal, that role assignment can fail in some cases. For example, if you use a script to create a new managed identity and then try to assign a role to that service principal, the role assignment might fail. The reason for this failure is likely a replication delay. The service principal is created in one region; however, the role assignment might occur in a different region that hasn't replicated the service principal yet. To address this scenario, you should specify the principal type when creating the role assignment.

```sh
az role assignment create --assignee-object-id "{assigneeObjectId}" \
--assignee-principal-type "{assigneePrincipalType}" \
--role "{roleNameOrId}" \
--resource-group "{resourceGroupName}" \
--scope "/subscriptions/{subscriptionId}"
```

For example,
```sh
az role assignment create --assignee-object-id "{service_principal_object_id}" \
--assignee-principal-type "ServicePrincipal" \
--role "Storage Blob Data Contributor" \
--resource-group "tfstate"
```

