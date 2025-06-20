resource "aws_db_subnet_group" "this" {
  name       = "default-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "default-subnet-group"
  }
}

resource "aws_db_instance" "this" {
  identifier               = var.db_name
  allocated_storage        = var.allocated_storage
  engine                   = var.engine
  engine_version           = var.engine_version
  instance_class           = var.instance_class
  db_name                  = var.db_name
  username                 = var.db_username
  password                 = var.db_password
  db_subnet_group_name     = aws_db_subnet_group.this.name

  vpc_security_group_ids   = var.security_group_ids

  parameter_group_name     = "default.postgres14"
  skip_final_snapshot      = true
  publicly_accessible      = true
  backup_retention_period  = 0
  deletion_protection      = false

  tags = {
    Environment = "dev"
  }
}
