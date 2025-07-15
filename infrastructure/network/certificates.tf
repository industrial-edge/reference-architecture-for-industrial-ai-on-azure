resource "tls_private_key" "dev" {
  count     = var.vnet_enabled ? 1 : 0
  algorithm = "RSA"
  rsa_bits  = "2048"
}

resource "tls_private_key" "client_cert" {
  count     = var.vnet_enabled ? 1 : 0
  algorithm = "RSA"
  rsa_bits  = "2048"
}

# The root certificate
resource "tls_self_signed_cert" "root_certificate" {
  count           = var.vnet_enabled ? 1 : 0
  private_key_pem = tls_private_key.dev[0].private_key_pem

  # 1 year validity
  validity_period_hours = 8766

  # Generate a new certificate if Terraform is run within three
  # hours of the certificate's expiration time.
  early_renewal_hours = 200

  is_ca_certificate = true

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
    "client_auth",
    "cert_signing"
  ]

  dns_names = [azurerm_public_ip.gateway[0].domain_name_label]

  subject {
    common_name  = "CAOpenVPN"
    organization = module.common.certificate_organization_name
  }
}

resource "local_file" "ca_pem" {
  count    = var.vnet_enabled ? 1 : 0
  filename = "caCert.pem"
  content  = tls_self_signed_cert.root_certificate[0].cert_pem
}

resource "null_resource" "cert_encode" {
  count = var.vnet_enabled ? 1 : 0
  provisioner "local-exec" {
    command = "openssl x509 -in caCert.pem -outform der | base64 -w0 > caCert.der"
  }

  # When running locally for interactive dev, this file remains between runs
  # On a build agent it doesn't persist across runs, but since the file output is deterministic
  # we can just recreate it each time
  triggers = {
    always_run = timestamp()
  }

  depends_on = [local_file.ca_pem]
}

data "local_file" "ca_der" {
  count    = var.vnet_enabled ? 1 : 0
  filename = "caCert.der"

  depends_on = [
    null_resource.cert_encode
  ]
}

resource "tls_cert_request" "client_cert" {
  count           = var.vnet_enabled ? 1 : 0
  private_key_pem = tls_private_key.client_cert[0].private_key_pem

  subject {
    common_name  = "ClientOpenVPN"
    organization = module.common.certificate_organization_name
  }
}

resource "tls_locally_signed_cert" "client_cert" {
  count              = var.vnet_enabled ? 1 : 0
  cert_request_pem   = tls_cert_request.client_cert[0].cert_request_pem
  ca_private_key_pem = tls_private_key.dev[0].private_key_pem
  ca_cert_pem        = tls_self_signed_cert.root_certificate[0].cert_pem

  validity_period_hours = 43800

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
    "key_encipherment",
    "client_auth"
  ]
}
