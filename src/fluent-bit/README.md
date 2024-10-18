<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# Client Cert authentication PoC
## Description
This is a PoC on how to generate and use certificates for authenticating forward inputs with client certificates between Fluent Bit instances.  
The setup consists of a source and a sink Fluent Bit instance. The source is configured to generate both metrics and logs.

## Setup
1. Generate client and server certificates as per [this guide](https://learn.microsoft.com/en-us/azure/application-gateway/self-signed-certificates). **When asked for ONs, ensure that the value for `fabrikam` and `contoso` is different.**
```
openssl ecparam -out contoso.key -name prime256v1 -genkey
openssl req -new -sha256 -key contoso.key -out contoso.csr
openssl x509 -req -sha256 -days 365 -in contoso.csr -signkey contoso.key -out contoso.crt
openssl ecparam -out fabrikam.key -name prime256v1 -genkey
openssl req -new -sha256 -key fabrikam.key -out fabrikam.csr
openssl x509 -req -in fabrikam.csr -CA  contoso.crt -CAkey contoso.key -CAcreateserial -out fabrikam.crt -days 365 -sha256
```
In this setup `contoso` will be both the client's root and server certificate, while `fabrikam` will be the client certificate.
2. Create a crt file for the client containing the full chain:
```
cat fabrikam.crt contoso.crt > chain.crt
```
3. Copy the certificate files into the Fluent Bit configuration folders:
```
cp fabrikam.* source/
cp chain.crt source/
cp contoso.crt source/

cp contoso.* sink/
```
4. Run the example:
```
docker compose up
```
The sink logs should show how both metrics and logs arrive.

## OpenTelemetry Collector

The ```opentel``` directory contains a gzipped OpenTelemetry Collector binary. This needs to be unzipped before use. To run the Collector, simply use

``` ./opentel/otelcol --config=./opentel/otel.yaml```

To see which Collector components are included in the build and at which version, inspect the accompanying manifest.yaml file.

The OTel Collector depends on an environment variable called APP_INSIGHTS_KEY. This is the Application Insights Instrumentation Key that can be found the Overview page of the Application Insights instance in the Azure Portal.
