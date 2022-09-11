provider "aws" {
  access_key = "access_key"
  secret_key = "scecret_key"
  region     = "us-east-2"
}

resource "aws_vpc" "terraform_vpc" {
  cidr_block           = "172.16.0.0/16"
  enable_dns_hostnames = true
  tags = {
    "name" = "tera_vpc"
  }
}

resource "aws_internet_gateway" "publie_gate" {
  vpc_id = aws_vpc.terraform_vpc.id
}

resource "aws_eip" "eip" {
  vpc = true
}
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.terraform_vpc.id
  cidr_block              = "172.16.1.0/24"
  availability_zone       = "us-east-2a"
  map_public_ip_on_launch = true
}
resource "aws_nat_gateway" "private_gate" {
  subnet_id     = aws_subnet.public_subnet.id
  allocation_id = aws_eip.eip.id

}

resource "aws_route_table" "public_table" {
  vpc_id = aws_vpc.terraform_vpc.id

}
resource "aws_route" "pub_table_route" {
  route_table_id         = aws_route_table.public_table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.publie_gate.id
}


resource "aws_route_table" "private_table" {
  vpc_id = aws_vpc.terraform_vpc.id

}
resource "aws_route" "pri_table_route" {
  route_table_id = aws_route_table.private_table.id
  destination_cidr_block     = "0.0.0.0/0"
  gateway_id     = aws_nat_gateway.private_gate.id
}

resource "aws_subnet" "private_subnet" {

  vpc_id                  = aws_vpc.terraform_vpc.id
  cidr_block              = "172.16.2.0/24"
  availability_zone       = "us-east-2a"
  map_public_ip_on_launch = false

}

resource "aws_route_table_association " "asso_route" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id =aws_route_table.public_table.id
}

resource "aws_route_table_association" "asso_route" {

  subnet_id      = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_table.id

}



resource "tls_private_key" "rsa_key" {
  algorithm = "RSA"
  rsa_bits =  4096
}
resource "aws_key_pair" "tera_key" {
  key_name = "tera_key"
  public_key= tls_private_key.rsa_key.public_key_openssh
}
resource "local_file" "key_file" {
  content = tls_private_key.rsa_key.private_key_pem
  filename = "${path.module}/tera_key.pem"
  
}



resource "aws_instance" "public_instance" {
  ami = "ami-0568773882d492fc8"
  instance_type = "t2.micro"
  #subnet_id = aws_subnet.public_subnet.id
  key_name = aws_key_pair.tera_key.id
  user_data = file("public_instance.sh")
}
resource "aws_instance" "private_instance" {
  ami = "ami-0568773882d492fc8"
  instance_type = "t2.micro"
  subnet_id = aws_subnet.private_subnet
  key_name = aws_key_pair.tera_key.id
  security_groups = [aws_security_group.security.Name]
}
resource "aws_security_group" "security" {
  name        = "tera_security"
  vpc_id      = aws_vpc.terraform_vpc.id

  ingress {
    description      = "HTTPS"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "HTTP"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "SSH"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = "tera_security"
  }
}
