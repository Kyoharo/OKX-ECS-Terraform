module "ecr" {
  source          = "../aws_ecr"
  component       = "ecr"         // Provide a value for component
  repository_name = "okx-app" // Provide a value for repository_name
}



locals {
  aws_region  = "us-west-2"
  aws_profile = "default"

  // ECR repository details
  ecr_repo    = module.ecr.repository_name
  ecr_reg     = module.ecr.repository_url
  aws_account = module.ecr.registry_id

  // Docker image details
  image_tag          = "1.0"
  dkr_img_src_path   = "${path.module}/docker-src"
  dkr_img_src_sha256 = sha256(join("", [for f in fileset(".", "${local.dkr_img_src_path}/**") : file(f)]))

  // Docker build and push command
  dkr_build_cmd = <<-EOT
    docker build -t ${local.ecr_repo}:${local.image_tag} ../../.

    docker tag ${local.ecr_repo}:${local.image_tag} ${local.aws_account}.dkr.ecr.${local.aws_region}.amazonaws.com/${local.ecr_repo}:${local.image_tag}

    aws --profile ${local.aws_profile} ecr get-login-password --region ${local.aws_region} | \
      docker login --username AWS --password-stdin ${local.aws_account}.dkr.ecr.${local.aws_region}.amazonaws.com/${local.ecr_repo}
    
      docker push ${local.aws_account}.dkr.ecr.${local.aws_region}.amazonaws.com/${local.ecr_repo}:${local.image_tag} 2>&1
  EOT
}

# Local-exec for build and push of docker image
resource "null_resource" "build_push_dkr_img" {
  triggers = {
    detect_docker_source_changes = var.force_image_rebuild == true ? timestamp() : local.dkr_img_src_sha256
  }

  provisioner "local-exec" {
    command = local.dkr_build_cmd
  }
}
