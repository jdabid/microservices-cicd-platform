output "cache_cluster_id" {
  description = "ID of the ElastiCache Redis cluster"
  value       = aws_elasticache_cluster.this.id
}

output "cache_nodes" {
  description = "List of cache node objects including id, address, port, and availability_zone"
  value       = aws_elasticache_cluster.this.cache_nodes
}

output "cache_endpoint" {
  description = "DNS name of the cache cluster without the port"
  value       = aws_elasticache_cluster.this.cache_nodes[0].address
}

output "cache_port" {
  description = "Port number of the cache cluster"
  value       = var.port
}

output "cache_security_group_id" {
  description = "Security group ID attached to the Redis cluster"
  value       = aws_security_group.redis.id
}
