terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# הגדרת ספק הענן (אמזון) והאזור (פרנקפורט)
provider "aws" {
  region = "eu-central-1"
}

# הגדרת חומת אש (Security Group)
resource "aws_security_group" "quantum_sg" {
  name        = "quantum_api_sg"
  description = "Allow port 5000 for Flask and 22 for SSH"

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# העלאת המפתח הפומבי שלנו ל-AWS כדי שנוכל להתחבר ב-SSH
resource "aws_key_pair" "quantum_keypair" {
  key_name   = "quantum_key"
  public_key = file("quantum_key.pub")
}

# מציאת הגרסה העדכנית ביותר של Ubuntu 22.04
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# יצירת השרת עצמו (EC2 Instance)
resource "aws_instance" "quantum_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro" 
  key_name               = aws_key_pair.quantum_keypair.key_name
  vpc_security_group_ids = [aws_security_group.quantum_sg.id]

  # סקריפט שרץ בהדלקה הראשונה: מתקין ומפעיל את Docker
  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y docker.io
              systemctl start docker
              systemctl enable docker
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "Quantum-Security-Server"
  }
}

# הדפסת כתובת ה-IP הציבורית של השרת החדש שלנו
output "server_public_ip" {
  value = aws_instance.quantum_server.public_ip
}