# Write-up - Jared Huna 

### Analyze, choose, and justify the appropriate resource option for deploying the app.

*For **both** a VM or App Service solution for the CMS app:*
- *Analyze costs, scalability, availability, and workflow*
- *Choose the appropriate solution (VM or App Service) for deploying the app*
- *Justify your choice*

## Why I use App Service as Appropiate Solution

- Azure App Service is a fully managed platform that enables developers to build websites, mobile backends, and web APIs for any platform or device.

- It provides built-in infrastructure management, including automatic maintenance, security patching, and scaling.

- Azure App Service supports multiple programming languages, such as .NET, .NET Core, Java, Ruby, Node.js, PHP, and Python. This application is developed using Python.

- It allows developers to quickly build, deploy, and scale web applications with minimal operational overhead.

## Justification w/ consideration to Cost-Scalability-Workflow

Cost Efficiency: Azure App Service is more cost-effective than using Virtual Machines. It offers multiple pricing plans, including Free and Shared (preview) tiers, which are ideal for testing or lightweight deployments. Additionally, App Service includes built-in load balancing, helping reduce overall infrastructure costs.


Scalability: Azure enables developers to easily scale applications both vertically and horizontally. Vertical scaling adjusts the resources allocated to the App Service—such as vCPUs and RAM—by changing the pricing tier. Horizontal scaling increases or decreases the number of Virtual Machine instances running the App Service to handle varying workloads.


Workflow - Azure App service can support automated deployments with GitHub, Azure DevOps and Git repository

### Assess app changes that would change your decision.

*Detail how the app and any other needs would have to change for you to change your decision in the last section.*

-If the app needed a custom operating system configuration, non-standard libraries, background services, or specific system-level dependencies that App Service does not support, a VM would be necessary. Azure VMs provide full control over the OS and installed software, whereas App Service abstracts these details away.



If the app relied on legacy frameworks, specific driver versions (for example, older ODBC drivers), or required direct access to the file system and server processes, App Service would be too restrictive. Azure VMs are designed to support legacy or lift‑and‑shift workloads that cannot easily be refactored for PaaS environments.


If the app required complex network setups such as custom firewalls, deep network inspection, custom ports, or tight integration with on‑prem infrastructure, a VM would be more appropriate. Azure VMs allow fine‑grained control over networking and security, while App Service limits this to simplified, managed configurations

