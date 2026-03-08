# NOTE: The S3 backend bucket and DynamoDB table must be created before
# running `terraform init`. Ensure the bucket name and DynamoDB table
# below match the actual resources provisioned in your AWS account.

terraform {
  backend "s3" {
    bucket         = "microservices-cicd-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}
