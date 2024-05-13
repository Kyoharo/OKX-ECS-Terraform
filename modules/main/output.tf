output "lb_dns_name" {
  value = aws_lb.LB.dns_name
}

output "repo_url" {
  value = "${local.aws_account}.dkr.ecr.${local.aws_region}.amazonaws.com/${local.ecr_repo}:${local.image_tag}"
  
}