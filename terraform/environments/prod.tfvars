# Production Environment Configuration
environment = "prod"
aws_region  = "us-east-1"

# VPC
vpc_cidr           = "10.1.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]

# EKS
cluster_version     = "1.28"
node_instance_types = ["t3.large"]
node_desired_size   = 3
node_min_size       = 2
node_max_size       = 6

# RDS
db_instance_class        = "db.t3.medium"
db_allocated_storage     = 50
db_max_allocated_storage = 200
db_multi_az              = true

# ElastiCache
cache_node_type = "cache.t3.small"
cache_num_nodes = 2
