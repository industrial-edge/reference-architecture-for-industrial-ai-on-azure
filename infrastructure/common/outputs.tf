output "rg_name" {
  value = var.deployment_source == "main" ? "rg-main" : format("rg-%s-%s", var.deployment_source, var.random_suffix)
}

output "vnet_name" {
  value = format("vnet-%s-%s", var.deployment_source, var.random_suffix)
}

output "private_dns_zone_group_name" {
  value = "private-dns-zone-group"
}

output "private_dns_resolver_name" {
  value = "private-dns-resolver"
}

output "certificate_organization_name" {
  value = "Siemens"
}

output "integration_subnet_name" {
  value = format("integration-subnet-%s-%s", var.deployment_source, var.random_suffix)
}

output "dns_resolver_subnet_name" {
  value = format("dns-resolver-subnet-%s-%s", var.deployment_source, var.random_suffix)
}

output "dns_resolver_inbound_endpoint_name" {
  value = format("dns-inbound-%s-%s", var.deployment_source, var.random_suffix)
}

output "vnet_peering_main_to_agent" {
  value = format("vp-%s-to-agent", var.deployment_source)
}

output "vnet_peering_agent_to_main" {
  value = format("vp-agent-to-%s", var.deployment_source)
}

output "vnet_gateway_ip_name" {
  value = format("vpn-gateway-ip-%s-%s", var.deployment_source, var.random_suffix)
}

output "vnet_gateway_name" {
  value = format("vpn-gateway-%s-%s", var.deployment_source, var.random_suffix)
}

output "kv_name" {
  value = format("kv-%s-%s", var.deployment_source, var.random_suffix)
}

output "kv_dns_vnet_link_name" {
  value = format("kv-%s-%s", var.deployment_source, var.random_suffix)
}

output "kv_dns_agent_vnet_link_name" {
  value = format("kv-agent-%s", var.random_suffix)
}

output "kv_private_endpoint_name" {
  value = format("pep-kv-%s-%s", var.deployment_source, var.random_suffix)
}

output "kv_private_service_connection_name" {
  value = format("psc-kv-%s-%s", var.deployment_source, var.random_suffix)
}

output "kv_logs_storage_account_name" {
  value = format("sakvlogs%s%s", var.deployment_source, var.random_suffix)
}

output "kv_monitor_diagnostic_setting_name" {
  value = format("kv-logs-%s-%s", var.deployment_source, var.random_suffix)
}

output "ampls_name" {
  value = format("ampls-%s-%s", var.deployment_source, var.random_suffix)
}

output "ampls_private_endpoint_name" {
  value = format("pep-ampls-%s-%s", var.deployment_source, var.random_suffix)
}

output "ampls_private_service_connection_name" {
  value = format("psc-ampls-%s-%s", var.deployment_source, var.random_suffix)
}

output "ampls_service_name_appinsights" {
  value = format("appinsights-amplsservice-%s-%s", var.deployment_source, var.random_suffix)
}

output "ampls_service_name_loganalyticsworkspace" {
  value = format("loganalyticsworkspace-amplsservice-%s-%s", var.deployment_source, var.random_suffix)
}

output "log_analytics_workspace_name" {
  value = format("loganalytics-%s-%s", var.deployment_source, var.random_suffix)
}

output "application_insights_name" {
  value = format("appinsights-%s-%s", var.deployment_source, var.random_suffix)
}

output "monitor_action_group_name" {
  value = format("monitor-ag-%s-%s", var.deployment_source, var.random_suffix)
}

output "failure_anomaly_name" {
  value = format("failure-anomaly-%s-%s", var.deployment_source, var.random_suffix)
}

output "kv_ai_connection_string_secret_name" {
  description = "The name of the secret stored in Key Vault containing the Application Insights connection string"
  value       = format("AppInsights-ConnectionString-%s", var.random_suffix)
}

output "kv_ai_application_id_secret_name" {
  description = "The name of the secret stored in Key Vault containing the Application Insights Id"
  value       = format("AppInsights-ApplicationId-%s", var.random_suffix)
}

output "kv_suffix_secret_name" {
  description = "The name of the secret stored in Key Vault containing the random suffix"
  value       = "KeyVault-Suffix"
}

## MLOps ##
output "ml_compute_cluster_subnet_name" {
  value = format("training-subnet-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_training_subnet_nsg_name" {
  value = format("training-nsg-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_dns_vnet_link_name" {
  value = format("azureml-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_dns_agent_vnet_link_name" {
  value = format("azureml-agent-%s", var.random_suffix)
}

output "ml_container_registry_name" {
  value = format("crml%s%s", var.deployment_source, var.random_suffix)
}

output "ml_storage_account_name" {
  value = format("saml%s%s", var.deployment_source, var.random_suffix)
}

output "ml_workspace_name" {
  value = format("mlws-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_user_assigned_identity_name" {
  value = format("umi-ml-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_compute_cluster_name" {
  value = format("compute-ml-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_workspace_private_endpoint_name" {
  value = format("pep-mlws-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_workspace_private_service_connection_name" {
  value = format("psc-mlws-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_container_registry_dns_vnet_link_name" {
  value = format("crml-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_container_registry_dns_agent_vnet_link_name" {
  value = format("crml-agent-%s", var.random_suffix)
}

output "ml_container_registry_private_endpoint_name" {
  value = format("pep-crml-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_container_registry_private_service_connection_name" {
  value = format("psc-crml-%s-%s", var.deployment_source, var.random_suffix)
}

output "kv_cr_name_secret_name" {
  description = "The name of the secret stored in Key Vault containing the name of the ML container registry"
  value       = format("ml-container-registry-name-%s", var.random_suffix)
}

##MLOps VNET##
output "ml_blobstorage_private_endpoint_name" {
  value = format("pe-ml-blobstorage-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_blobstorage_private_service_connection_name" {
  value = format("psc-ml-blobstorage-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_blobstorage_dnszone_vnetlink_name" {
  value = format("dns-link-ml-blobstorage-%s-%s", var.deployment_source, var.random_suffix)
}

output "ml_blobstorage_dnszone_agent_vnetlink_name" {
  value = format("dns-link-ml-blobstorage-agent-%s", var.random_suffix)
}
## IoT Management ##
output "iothub_name" {
  value = format("iothub-%s-%s", var.deployment_source, var.random_suffix)
}

output "kv_iothub_connection_string_secret_name" {
  description = "The name of the secret stored in Key Vault containing the IoT Hub connection string"
  value       = format("iotmngmt-iothub-primary-connection-string-%s", var.random_suffix)
}

output "kv_iothub_name_secret_name" {
  description = "The name of the secret stored in Key Vault containing the IoT Hub name"
  value       = format("iotmngmt-iothub-name-%s", var.random_suffix)
}

output "kv_iothub_eventhubendpoint_secret_name" {
  description = "The name of the secret stored in Key Vault containing the IoT Hub Event Hub Endpoint"
  value       = format("iotmngmt-iothub-eventhubendpoint-%s", var.random_suffix)

}

output "kv_eventhub_compatible_endpoint_secret_name" {
  description = "The name of the secret stored in Key Vault containing the Event Hub compatible endpoint"
  value       = format("iotmngmt-iothub-eventhub-compatible-endpoint-%s", var.random_suffix)
}

## IoT Management VNET ##
output "iothub_dns_vnet_link_name" {
  value = format("iothub-%s-%s", var.deployment_source, var.random_suffix)
}

output "eventhub_dns_vnet_link_name" {
  value = format("eventhub-%s-%s", var.deployment_source, var.random_suffix)
}

output "iothub_dns_agent_vnet_link_name" {
  value = format("iothub-agent-%s", var.random_suffix)
}

output "eventhub_dns_agent_vnet_link_name" {
  value = format("eventhub-agent-%s", var.random_suffix)
}

output "iot_hub_private_service_connection_name" {
  value = format("psc-iothub-%s-%s", var.deployment_source, var.random_suffix)
}

output "iot_hub_private_endpoint_name" {
  value = format("pep-iothub-%s-%s", var.deployment_source, var.random_suffix)
}

#### Self Hosted Agents ####

output "agent_rg_name" {
  value = "rg-agent"
}

output "agent_vnet_name" {
  value = "vnet-agent"
}

output "agent_default_subnet_name" {
  value = "default-subnet-agent"
}

output "agent_vm_scaleset_name" {
  value = "vm-scaleset-agent"
}

output "agent_vm_scaleset_extension_name" {
  value = "vm-scaleset-agent-extension"
}

output "agent_network_interface" {
  value = "agent-network-interface"
}

output "agent_public_ip" {
  value = "agent-public-ip"
}
