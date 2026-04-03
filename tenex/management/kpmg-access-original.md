Access and People
How many Tenex developers will be working on this? 4-6
What are their email addresses so we can provision access? dan@tenex.co, brandon@tenex.co, scott@tenex.co, cj@tenex.co, jason@tenex.co
Source Control and Tooling
Do you expect us to provide GitHub, or do you already have your own? Are you okay with Azure repository?
We prefer GitHub for source control as our team's tooling, AI workflows, and CI/CD are built around it. Ideally, we'd work within a client-provided GitHub organization so everything lives in your ecosystem.
Azure and Infrastructure
What Azure services do you actually need? 
Data services
Package hosting
Caching or memcache
Any other platform services
AI services / expected token usage
Based on our standard architecture, we anticipate needing the following:
Compute
Azure Container Apps — for hosting backend services (serverless containers with autoscaling)
Data Services
Azure Database for PostgreSQL – Flexible Server — primary relational database
Azure Blob Storage — file and object storage
Caching
Azure Managed Redis — in-memory caching and session management
Package / Artifact Hosting
Azure Container Registry — for storing and managing container images
Platform Services
Azure Key Vault — secrets and credential management
Azure Monitor / Application Insights — observability, logging, and alerting
Azure Virtual Network — network isolation and security
We'll refine this list once we're deeper into the project requirements, but the above should cover the core infrastructure. If there are preferred tiers or existing resource groups you'd like us to work within, we're happy to adapt.
AI Services / Expected Token Usage
We'll forecast AI costs early based on expected usage patterns, volume, and model pricing, and work with you to target a cost envelope that fits your budget. The key tradeoff is model capability versus latency and cost. Some workflows warrant the most capable models and longer running tasks, while others are better served by faster, cheaper alternatives. We'll design accordingly and optimize to your needs as we scope the project and as real usage data comes in, designing our architecture with cost flexibility in mind.
For maximum development velocity, it's extremely helpful when clients can provide AI coding tool accounts (i.e. Claude Code, Cursor) for the team. This gives us access to the best-in-class models for code generation, review, and iteration, which meaningfully accelerates delivery when we are unconstrained by token usage. This isn't a hard requirement, but in our experience it's one of the highest-leverage investments a client can make in the speed and quality of our output. If this is something you're open to, we can share specifics on what we'd need.
Other Dependencies
Is there anything else you need from us that we're not thinking about yet? 

The specifics will depend on the project, but we typically need access to:
Any systems of record or internal APIs the project will integrate with (e.g., CRMs, ERPs, billing systems, identity providers)
Staging or sandbox environments for third-party services we'll be connecting to
Sample data or test accounts to develop and validate against realistic scenarios
Documentation for any proprietary internal systems or protocols


Are you using your own Jira and other licensed tools to manage the work? 
We use Linear for project management as our source of record.
Contact
Who would be the technical contact to follow up with if we need assistance?
Dan Zakon (dan@tenex.co)
Straightforward swaps. Want me to format this as a doc you can attach to that email to Brett?


