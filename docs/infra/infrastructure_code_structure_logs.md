# Infrastructure code structure for logs

# Introduction
The document describes the infrastructure resources required to be deployed in order to enable sending data to Log Analytics Workspace using the Logs Ingestion API in Azure Monitor (Azure Monitor can collect data from multiple sources, even from Custom Sources as it is the case here).

## Components overview
The resource are created as part of the metrics_and_logs module.
The Logs Ingestion API in Azure Monitor requires the following specific resources to be created before data can be sent:
* Data Collection Endpoint (DCE): the DCE provides an endpoint for the application (in our case the Logs Function) to send data to; a single DCE can support multiple DCRs
* Data Collection Rule: the DCR defines data collected by Azure Monitor and specifies how and where the data should be stored
* Log Analytics Workspace – the workspace contains the tables that will receive the data;  it can either be an existing Azure table (i.e syslog) or a custom table; in our case a custom table is used; the custom table name must have the “_CL” suffix; column names must start with a letter and can consist of up to 45 alphanumeric characters and the “_”  or “ –“ characters

```text
infrastructure
|__ metrics_and_logs
        |__ main.tf
            * Log Analytics Workspace
            * Storage Account (linked to the log analytics workspace)
            * Logs Function App
            * Storage Account (for the logs function app)
            * Azure Monitor Data Collection Endpoint
            * Azure Monitor Data Collection Rule
            * Custom Log Table (part of the log analytics workspace)
            ...
```


## Basic flow
* When the logs function part of the metrics and logs function app is triggered it sends data to the DCE (Data Collection Endpoint)
* The HTTP call specifies the  DCR (Data Collection Rule) that understands the format of the source data (potentially filters and transforms the data for the target table), directs the data to a specific table in a specific workspace;
* the payload of the API call includes the source data in JSON format and must match the structure expected by the DCR; it does not necessarily need to match the structure of the target table as the DCR can include a transformation to convert the data to match the table’s structure

```text
trigger ---> Logs Function --Http POST(data)--> DCE --data--> DCR --transformed data--> Custom Logs Table (in Logs Analytics Workspace)
```

Some remarks:
* The API call that the function makes must specify a DCR to use (in our case the function is using a client library for Python to create a LogsIngestionClient  instance, client that uses the DCR immutable ID stored in KV to identify the DCR to use);  
* The DCR needs to understand the structure of the input data and the structure of the target table; if the two do not match it can include transformations to convert the source data to match the target table (in our case this is achieved through the data flow’s stream declaration when creating the DCR terraform resource)

More information specific to the logs function implementation can be found in the README file located at /aeworkspace/src/functions/README.md
