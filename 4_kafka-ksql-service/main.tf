/*
Terraform AWS example
awscli가 설치되어 있고, Access Key, Secret Key가 등록되어 있어야 한다.
*/
######################################################################
# Provisioning
######################################################################
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 0.14.9"
}

# setup to specified provider
provider "aws" {
  profile = "default"
  region  = "ap-northeast-2" # seoul region
}

######################################################################
# Set Up Security Groups
######################################################################
# 보안그룹 생성 or 수정
resource "aws_security_group" "basic_sgroup"{
  name = "yunan_basic_sgroup"
  # Inbound Rule 1
  ingress {
    # from, to로 포트 허용 범위를 나타낸다.
    from_port = 22
    to_port = 22
    description = "for ssh connection"
    protocol = "tcp"
    cidr_blocks = var.my_ip_list
  }

  egress{ # 인스턴스에서 외부로 나가는 request 모두 허용. 이를 없애면 유사 IDC환경 테스트 가능.
    description = "allows all outbound (apt, ping, ...)"
    protocol  = "-1"
    from_port = 0
    to_port   = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "kafka_sgroup"{
  name = "yunan_kafka_sgroup"
  ingress {
    from_port = 9092
    to_port = 9092
    description = "for kafka communication"
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port = 8083
    to_port = 8083
    description = "for kafka connect"
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port = 8080
    to_port = 8080
    description = "for kafka monitoring"
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

######################################################################
# Set Up Basic Instance
######################################################################
resource "aws_instance" "basic" {
  ami           = var.ami
  instance_type = var.instance_type
  tags = merge(var.tags, {Name = var.tag_name}, )
  key_name = var.key_pair_name
  security_groups = [
    aws_security_group.basic_sgroup.name,
    aws_security_group.kafka_sgroup.name,
  ]
}

data "template_file" "kafka_properties" {
  template = file("${path.module}/config/server.properties")
  vars = {
    AWS-PUBLIC-DNS-OR-HOSTNAME-HERE = aws_instance.basic.public_dns
  }
}
data "template_file" "connect_service" {
  template = file("${path.module}/config/connect.service")
  vars = {
    AWS-ACCESS-KEY-HERE = var.aws_access_key
    AWS-SECRET-KEY-HERE = var.aws_secret_key
  }
}

#################################################
# Basic Commands
#################################################
resource "null_resource" "basic_remote"{

  # remote-exec를 위한 ssh connection 셋업
  connection {
    type = "ssh"
    host = aws_instance.basic.public_ip
    user = "ubuntu"
    private_key = file(var.private_key_path)
    agent = false
  }

  provisioner "file"{
    source = "${path.module}/config"
    destination = "/home/ubuntu/config"
  }
  provisioner "file" {
    content = data.template_file.kafka_properties.rendered
    destination = "/home/ubuntu/config/server.properties"
  }
  provisioner "file"{
    content = data.template_file.connect_service.rendered
    destination = "/home/ubuntu/config/connect.service"
  }

  # 실행된 원격 인스턴스에서 수행할 cli명령어
  provisioner "remote-exec" {
    inline = [
      "cloud-init status --wait",
      # JDK
      "sudo apt update ; sudo apt install -y openjdk-8-jdk-headless",

      # Kafka 설치
      "wget ${var.kafka_index}  &&  tar xvf ~/${var.kafka_ver}.tgz",
      "sudo mv ~/${var.kafka_ver}/ /usr/local/kafka/",  # 디렉토리 이름을 kafka로 변경하면서 이동
      "sudo mv ~/config/*.properties /usr/local/kafka/config/",

      # 필요 커넥터 설치
      "wget ${var.jdbc_con_index} ${var.s3_con_index}",
      "sudo apt install unzip  &&  unzip '*.zip'",
      "sudo mkdir -p /opt/connectors",
      "sudo mv ~/confluentinc-kafka-connect-*/  /opt/connectors/",

      # ksqldb
      "chmod +x ~/config/install_ksqldb.sh",
      "sudo ~/config/install_ksqldb.sh",

      # 서비스등록 (zookeeper, broker, connect, ksqldb)
      "sudo mv ~/config/*.service /etc/systemd/system/",
      "sudo systemctl daemon-reload",
      "sudo systemctl restart broker.service connect.service ksqldb.service",  # zookeeper는 broker의 requires로 실행
    ]
  }
}

