# Development Environment Configuration
environment = "dev"
aws_region  = "us-east-1"

# VPC
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]

# EKS
cluster_version     = "1.28"
node_instance_types = ["t3.medium"]
node_desired_size   = 1
node_min_size       = 1
node_max_size       = 2

# RDS
db_instance_class        = "db.t3.micro"
db_allocated_storage     = 20
db_max_allocated_storage = 50
db_multi_az              = false

# ElastiCache
cache_node_type = "cache.t3.micro"
cache_num_nodes = 1
