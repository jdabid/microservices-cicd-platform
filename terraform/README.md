# Infrastructure as Code - Terraform

AWS infrastructure for the Medical Appointments Microservices Platform, managed entirely with Terraform. The setup provisions a production-ready Kubernetes environment with managed database and caching layers across two isolated environments (dev and prod).

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────┐
                    │                    AWS Cloud                     │
                    │  ┌──────────────────────────────────────────┐   │
                    │  │              VPC (10.0.0.0/16)           │   │
                    │  │                                          │   │
                    │  │  ┌─────────────┐   ┌─────────────┐      │   │
                    │  │  │ Public      │   │ Public      │      │   │
                    │  │  │ Subnet 1a   │   │ Subnet 1b   │      │   │
                    │  │  │ 10.0.1.0/24 │   │ 10.0.2.0/24 │      │   │
                    │  │  └──────┬──────┘   └──────┬──────┘      │   │
                    │  │         │    ┌──────┐     │              │   │
                    │  │         └────│  NAT │─────┘              │   │
                    │  │              │  GW  │                    │   │
                    │  │              └──┬───┘                    │   │
                    │  │                │                         │   │
                    │  │  ┌─────────────┴─┐   ┌─────────────┐    │   │
                    │  │  │ Private       │   │ Private      │   │   │
                    │  │  │ Subnet 1a     │   │ Subnet 1b    │   │   │
                    │  │  │ 10.0.10.0/24  │   │ 10.0.20.0/24 │   │   │
                    │  │  │               │   │              │    │   │
                    │  │  │  ┌─────────┐  │   │ ┌─────────┐  │   │   │
                    │  │  │  │   EKS   │  │   │ │   EKS   │  │   │   │
                    │  │  │  │  Nodes  │  │   │ │  Nodes  │  │   │   │
                    │  │  │  └─────────┘  │   │ └─────────┘  │   │   │
                    │  │  │               │   │              │    │   │
                    │  │  │  ┌─────────┐  │   │              │   │   │
                    │  │  │  │   RDS   │  │   │              │    │   │
                    │  │  │  │ (PG 15) │  │   │              │   │   │
                    │  │  │  └─────────┘  │   │              │    │   │
                    │  │  │               │   │              │    │   │
                    │  │  │  ┌─────────┐  │   │              │   │   │
                    │  │  │  │  Redis  │  │   │              │    │   │
                    │  │  │  │ (EC)    │  │   │              │   │   │
                    │  │  │  └─────────┘  │   │              │    │   │
                    │  │  └───────────────┘   └──────────────┘   │   │
                    │  └──────────────────────────────────────────┘   │
                    └─────────────────────────────────────────────────┘
```

## Modules

| Module | Description |
|--------|-------------|
| **vpc** | VPC with public and private subnets across 2 AZs, NAT Gateway, Internet Gateway, and route tables |
| **eks** | EKS cluster with managed node groups running in private subnets |
| **rds** | PostgreSQL 15 RDS instance in a private subnet group with automated backups |
| **elasticache** | Redis ElastiCache cluster in private subnets for session caching and Celery broker |

## Prerequisites

- **AWS CLI** v2 configured with appropriate IAM credentials
- **Terraform** >= 1.5
- **S3 bucket** for remote state storage (e.g., `microservices-cicd-tfstate`)
- **DynamoDB table** for state locking (e.g., `terraform-lock`)
- **kubectl** for post-deployment cluster access

## Usage

Initialize the Terraform working directory:

```bash
terraform init
```

Preview changes for the target environment:

```bash
# Development
terraform plan -var-file=environments/dev.tfvars

# Production
terraform plan -var-file=environments/prod.tfvars
```

Apply the infrastructure:

```bash
# Development
terraform apply -var-file=environments/dev.tfvars

# Production
terraform apply -var-file=environments/prod.tfvars
```

Destroy the infrastructure (use with caution):

```bash
terraform destroy -var-file=environments/dev.tfvars
```

## Environment Differences

| Resource | Dev | Prod |
|----------|-----|------|
| VPC CIDR | 10.0.0.0/16 | 10.1.0.0/16 |
| EKS Node Type | t3.medium | t3.large |
| EKS Node Count | 1 (max 2) | 3 (max 6) |
| RDS Instance | db.t3.micro | db.t3.medium |
| RDS Storage | 20 GB (max 50) | 50 GB (max 200) |
| RDS Multi-AZ | No | Yes |
| ElastiCache Type | cache.t3.micro | cache.t3.small |
| ElastiCache Nodes | 1 | 2 |

## State Management

Terraform state is stored remotely in an S3 bucket with DynamoDB-based locking to prevent concurrent modifications:

```hcl
backend "s3" {
  bucket         = "microservices-cicd-tfstate"
  key            = "infrastructure/terraform.tfstate"
  region         = "us-east-1"
  dynamodb_table = "terraform-lock"
  encrypt        = true
}
```

- **S3** provides durable, versioned state storage with server-side encryption
- **DynamoDB** provides a locking mechanism that prevents race conditions when multiple engineers run Terraform simultaneously

## Security Considerations

- All sensitive variables (database passwords, API keys) are marked with `sensitive = true` in variable definitions
- No plaintext secrets are stored in `.tfvars` files or the repository -- use AWS Secrets Manager or SSM Parameter Store
- RDS and ElastiCache are deployed in private subnets with no public access
- EKS worker nodes run in private subnets; only the API server endpoint is public
- S3 state bucket has encryption enabled (`encrypt = true`)
- All storage resources (RDS, S3) use encryption at rest
- Security groups follow the principle of least privilege, allowing only required traffic between services
