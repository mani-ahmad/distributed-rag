# output "backend_url" {
#   description = "Public HTTP endpoint of the backend ALB"
#   value       = "http://${module.ecs_backend.alb_dns_name}"
# }

output "alb_dns_name" {
  value       = aws_lb.this.dns_name
  description = "DNS of the ALB"
}