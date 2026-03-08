# ADR-002: Modular Terraform for Infrastructure as Code

## Status
Accepted

## Date
2026-03-10

## Context
The platform requires cloud infrastructure provisioning for multiple environments (development, staging, production). The infrastructure includes:

- **Networking**: VPC with public/private subnets across availability zones.
- **Compute**: EKS (Elastic Kubernetes Service) cluster for running containerized workloads.
- **Database**: RDS PostgreSQL instance for persistent data storage.
- **Caching**: ElastiCache Redis for session management, caching, and Celery broker.

Key requirements:
- Infrastructure must be reproducible and version-controlled.
- Multiple environments must share the same infrastructure definition with different parameters.
- State must be managed safely across team members and CI/CD pipelines.
- Resources must follow security best practices (private subnets, encryption, least-privilege IAM).

## Decision
Use Terraform with a modular architecture. Each infrastructure component is an independent, reusable module with per-environment variable files.

### Module Structure

```
terraform/
  main.tf              # Root module composing all child modules
  variables.tf         # Input variables for the root module
  outputs.tf           # Outputs exposed from the root module
  providers.tf         # AWS provider configuration
  versions.tf          # Terraform and provider version constraints
  modules/
    vpc/               # Network: VPC, subnets, NAT, route tables
    eks/               # Compute: EKS cluster, node groups, IRSA
    rds/               # Database: PostgreSQL instance, subnet group
    elasticache/       # Cache: Redis cluster, subnet group
  environments/
    dev.tfvars          # Development environment parameters
    prod.tfvars         # Production environment parameters
```

### State Management
- **Backend**: S3 bucket for state storage with versioning enabled.
- **Locking**: DynamoDB table for state locking to prevent concurrent modifications.
- **Encryption**: State files encrypted at rest using S3 server-side encryption.

### Module Design Principles
- Each module exposes clearly typed input variables with descriptions.
- Each module produces outputs that other modules can reference.
- Sensitive variables (database passwords, API keys) are marked `sensitive = true`.
- Modules use `for_each` or `count` where appropriate for multi-AZ resources.

## Consequences

### Positive
- **Environment parity**: The same module definitions are used across dev and prod, reducing configuration drift. Only variable values differ.
- **Reusability**: Modules can be extracted and reused in other projects or shared across teams.
- **Auditability**: All infrastructure changes are tracked in Git with full diff visibility.
- **Safe collaboration**: S3 + DynamoDB backend ensures only one apply runs at a time and state is never lost.
- **Multi-cloud potential**: Terraform supports multiple providers, so the modular approach can extend to GCP or Azure if needed.

### Negative
- **State management overhead**: The S3 backend and DynamoDB table must be bootstrapped manually before Terraform can be used.
- **Learning curve**: Terraform's HCL syntax, state model, and plan/apply workflow require onboarding time for new contributors.
- **Module versioning**: As modules evolve, breaking changes must be coordinated across environments. No built-in module registry is used (modules are local).
- **Blast radius**: A misconfigured root module apply could affect multiple infrastructure components simultaneously.

### Risks
- **State corruption**: If the S3 backend is misconfigured or the DynamoDB lock fails, concurrent applies could corrupt state. Mitigation: CI/CD pipelines serialize Terraform operations.
- **Credential exposure**: Terraform state may contain sensitive values in plaintext. Mitigation: S3 encryption at rest, restricted bucket policies, and `sensitive = true` on variables.
- **Provider version drift**: Upgrading the AWS provider may introduce breaking changes. Mitigation: Pin provider versions in `versions.tf`.

## Alternatives Considered

### AWS CloudFormation
AWS-native IaC using JSON/YAML templates.
- **Rejected because**: Locked to AWS, reducing portability. Template syntax is verbose compared to HCL. Lacks the rich module ecosystem and community tooling (e.g., `tflint`, `checkov`) that Terraform provides.

### Pulumi
IaC using general-purpose programming languages (Python, TypeScript).
- **Rejected because**: Adds a runtime dependency and SDK. The team is more familiar with declarative HCL than imperative IaC. Pulumi's state management (Pulumi Cloud or self-hosted) adds another service to operate.

### AWS CDK
Cloud Development Kit using TypeScript/Python to synthesize CloudFormation templates.
- **Rejected because**: Still generates CloudFormation under the hood, inheriting its limitations. Adds a build/synthesis step. Locked to AWS.

### Manual Console / CLI
Provision resources manually through the AWS Console or CLI scripts.
- **Rejected because**: Not reproducible, not auditable, and error-prone. Does not support environment parity or rollback.
