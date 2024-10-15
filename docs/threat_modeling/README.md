# Threat Modeling

This folder contains the data flow diagrams created using the [Microsoft Threat Modeling Tool](https://learn.microsoft.com/en-gb/azure/security/develop/threat-modeling-tool). In order to view / edit the diagrams or the generated list of threats you need to open these models inside the tool.
The list of threats is also documented on the project's ADO wiki for planning purposes.

The list data flow scenarios for the current system is:

- MLOps and E2C/C2E communication using IoT Hub
![ml-dfd](./imgs/ml-dataflow-diagram.png)
- IoT Hub certificate management
![iot-cert-management-dfd](./imgs/iot_certmanagement_dfd.png)
- Metrics and Logs
![met-and-logs-dfd](./imgs/metlogs-dfd.png)
- Authentication Proxy certificate management
![auth-proxy-dfd](./imgs/authproxy_dfd.png)
