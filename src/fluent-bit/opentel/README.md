<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# README

This document describes how we build/update the OpenTelemetry Collector (OtelCol) used by this engagement.

The Collector will be built based on the `manifest.yaml` file held in the Siemens repo at `{Siemens-Microsoft-IAI-Reference Repo}/src/fluent-bit/opentel/manifest.yaml`

If editing this, updating the release, or adding new components, the full [Contrib](https://github.com/open-telemetry/opentelemetry-collector-releases/blob/main/distributions/otelcol-contrib/manifest.yaml) manifest is a useful resource to use.

To create a new `otelcol` executable:

- Ensure `{Siemens-Microsoft-IAI-Reference Repo}/src/fluent-bit/opentel/manifest.yaml` contains the version/components you want to include.

- Clone the [OpenTelemetry-Collector](https://github.com/open-telemetry/opentelemetry-collector) repo locally.

- In the root of the repo, type `make ocb` - this will make the OpenTelemetry Builder which is used to build the `otelcol` exe.

- `cd` into the `bin` folder that has been created. It should contain an executable called `ocb_linux_amd64` (or equivalent for your local architecture).

- Now issue the command `./ocb_linux_amd64 --config {Siemens-Microsoft-IAI-Reference Repo}/src/fluent-bit/opentel/manifest.yaml`

- This will build a custom exe and write it to `./_build/otelcol` - this is the custom OtelCollector to use, so copy it to wherever it is to be used.