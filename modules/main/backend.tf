
# Configure the Terraform backend to store state information in S3
terraform {
  backend "s3" {
    bucket  = "terraform-state-kyoharo"
    key     = "devops/terraform.tfstate" # Replace with the desired key name for your state file
    region  = "us-west-2"
    encrypt = true
  }
  required_version = ">=0.13.0"
  required_providers {
    aws = {
      version = ">=2.7.0"
      source  = "hashicorp/aws"
    }
  }
}