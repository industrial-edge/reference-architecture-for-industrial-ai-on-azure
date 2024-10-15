# Well Architected Framework Alignment

This page describes how this application has addressed each of the pillars defined in the [Azure Well Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/) (WAF).

The WAF is built upon 5 pillars

| Pillar |	Description|
|--------|-------------|
|Reliability |	The ability of a system to recover from failures and continue to function.|
|Security	|Protecting applications and data from threats.|
|Cost optimization |	Managing costs to maximize the value delivered.|
|Operational excellence |	Operations processes that keep a system running in production.|
|Performance efficiency	|The ability of a system to adapt to changes in load.|

## Reliability

| Principle | Current Position | Possible Improvements |
|-----------|------------------|-----------------------|
| Design for Business Requirements | No reliability requirements have been defined during this pilot phase. | Could define SLO/SLA for the application as a whole. |
| Design for Failure |  OpenTelemetry Collector has persisted retry policies. | Examine other system components for resiliency improvements. |
| Observe Application Health | Azure components are monitored. Azure based observability has been implemented for edge models through AI Model Monitor. | Investigate whether other edge components (including Model Manager and Model Monitor) can be remotely monitored. |
| Drive automation | Increasing number of processes in the application have been automated via Azure DevOps pipelines | |
| Design for self-healing | Not relevant to this application | |
| Design for scale-out | Not addressed | Consider whether any of the Edge or Azure components can be scaled. If so, determine the conditions under which this should happen. |

## Security

| Principle | Current Position | Possible Improvements |
|-----------|------------------|-----------------------|
| Plan resources and how to harden them | Improved from baseline | |
| Automate and use least privilege | Improved significantly from baseline | |
| Classify and encrypt data | Certificate and application secrets are now held in Azure KeyVault. Logs and Metrics data is stored in Azure Monitor. All data transfer from factory to cloud is encrypted in transit. | |
| Monitor system security, plan incident response | Azure Monitor is now used to store/process logs & metrics data. No alerts have been configured. No Incident Response planning has taken place. | <ul><li> Correlate security and audit events to model application health.</li> <li>Correlate security and audit events to identify active threats. </li><li> Establish automated and manual procedures to respond to incidents. </li><li>Use security information and event management (SIEM) tooling for tracking.</li></ul> | |
| Identify and protect endpoints | All public endpoints removed. Access to vNet resources is by VPN Gateway only. | |
| Protect against code-level vulnerabilities | Limited action | Introduce CI/CD pipeline checks such as CredScan and package vulnerability scanning. |
| Model and test against potential threats | [Threat Model complete](https://dev.azure.com/siemens-microsoft-iai/Siemens-Microsoft-IAI/_git/Siemens-Microsoft-IAI-Reference?path=/docs/threat_modeling/README.md&version=GBdevelopment&_a=contents). | Static code analysis, CredScan and penetration testing should be considered. |

## Cost Optimisation

| Principle | Current Position | Possible Improvements |
|-----------|------------------|-----------------------|
| Choose the correct resources | Correct resources are in use, smallest scale SKU by default | |
| Set up budgets and maintain cost constraints | No action taken | Build a cost model, set budgets and alerts in Azure.|
| Dynamically allocate and deallocate resources | Single instance of all resources by default. Azure ML auto-scales back to 0 instances when not in use. | Investigate auto-scale options.  |
| Optimise workloads, aim for scalable costs | Not applicable? No real Azure based workloads? |  |
| Continuously monitor and optimise cost management | No action taken | <ul><li>Conduct regular cost reviews</li><li>Measure capacity needs</li><li>Forecast capacity needs</li></ul> |

## Operational Excellence

| Principle | Current Position | Possible Improvements |
|-----------|------------------|-----------------------|
| Optimise Build and Release processes | Implementation of Infrastructure as Code, CI/CD pipelines. Moved to GitFlow for branch management. | Could improve automated testing |
| Understand operational health | No action taken | Monitor build/release pipelines, infrastructure and application health |
| Rehearse recovery and practice failure | No action taken | Define a Disaster Recovery Plan |
| Embrace continuous operational improvement | No action taken | <ul><li>Evolve processes over time.</li><li>Optimize inefficiencies and associated processes.</li><li>Learn from failures.</li><li>Continuously evaluate new opportunities.</li></ul>|
| Use loosely coupled architecture | No specific action taken | |

## Performance

| Principle | Current Position | Possible Improvements |
|-----------|------------------|-----------------------|
| Design for horizontal scaling | No action taken | <ul><li>Define capacity model against requirements. </li><li>Define autoscaling to manage it</li></ul> |
| Shift-left on performance testing | No performance testing undertaken | <ul><li>Run load/stress tests</li><li>Establish performance baseline</li><li>Test in CI/CD pipelines</li></ul> |
| Continuously monitor performance in production | No action taken | Monitor health of complete application. |
