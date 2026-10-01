variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "reto-sysops"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
  default     = "10.20.0.0/16"
}

variable "container_port" {
  description = "FastAPI container port"
  type        = number
  default     = 8000
}

variable "ecs_desired_count" {
  description = "Number of ECS tasks"
  type        = number
  default     = 1
}

variable "container_image" {
  description = "Container image used by ECS"
  type        = string
  default     = "468579857064.dkr.ecr.us-east-1.amazonaws.com/reto-sysops-dev-api:v3"
}
