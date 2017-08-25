variable "profile" {
  description = "AWS credentials profile name."
  default     = "saml"
}

variable "region" {
  description = "AWS region in which to create resources."
  default     = "us-east-1"
}

variable "workgroup" {
  description = "Resource 'Workgroup' tag value."
  default     = "dbhi"
}

variable "project" {
  description = "Resource 'Project' tag value."
  default     = "dmsqla"
}

variable "private_cidr" {
  description = "CHOP network private CIDR."
  default     = "159.14.0.0/16"
}

variable "instance_type" {
  description = "Size of the instance."
  default     = "t2.nano"
}

variable "ssh_key_name" {
  description = "Name of the key to use for SSH access."
  default     = "DBHiKey"
}

variable "vpc_remote_state_environment" {
  description = "Name of the state environment where the VPC remote state is stored."
  default     = "default"
}

variable "vpc_remote_state_bucket" {
  description = "Name of the S3 bucket where the VPC remote state is stored."
  default     = "chop-dbhi-terraform"
}

variable "vpc_remote_state_key" {
  description = "Path to the S3 bucket object where the VPC remote state is stored."
  default     = "network.tfstate"
}
