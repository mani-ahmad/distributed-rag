//RDS
variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "engine" {
  description = "The database engine to use"
  type        = string
  default     = "postgres"
}

variable "engine_version" {
  description = "Version of the database engine"
  type        = string
  default     = "14.13"
}

variable "instance_class" {
  description = "Instance class (must be free-tier eligible)"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Name of the initial database"
  type        = string
}

variable "db_username" {
  description = "Master username for RDS"
  type        = string
  default     = "mani"
}

variable "db_password" {
  description = "Master password for RDS"
  type        = string
  sensitive   = true
}

variable "security_group_ids" {
  description = "List of security group IDs to assign to RDS"
  type        = list(string)
}

variable "subnet_ids" {
  description = "List of subnet IDs for RDS"
  type        = list(string)
}


