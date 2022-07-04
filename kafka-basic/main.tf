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

  # Outbound Rule 1 (아래 예시는 설정하지 않은것과 같은, 전체 허용 표기법이다.)
  egress{
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

  provisioner "file" {
    content = data.template_file.kafka_properties.rendered
    destination = "/home/ubuntu/server.properties"
  }
  # 실행된 원격 인스턴스에서 수행할 cli명령어
  provisioner "remote-exec" {
    inline = [
      "cloud-init status --wait", # cloud-init이 끝날 떄 까지 기다린다. 에러 예방 차원에서 항상 써준다.
      "mkdir test-make-instance",
      "sudo apt update",
      "yes | sudo apt install openjdk-8-jdk-headless",
      "wget https://dlcdn.apache.org/kafka/3.2.0/${var.kafka_ver}.tgz",
      "tar xvf ${var.kafka_ver}.tgz",

      # 카프카 힙메모리 설정
      "export KAFKA_HEAP_OPTS='-Xmx400m -Xms400m'",
      "echo \"export KAFKA_HEAP_OPTS='-Xmx400m -Xms400m'\" >> ~/.bashrc",  # source 명령어는 안됨.

      # 주키퍼 실행
      "${var.kafka_ver}/bin/zookeeper-server-start.sh -daemon ${var.kafka_ver}/config/zookeeper.properties",

      # 카프카 브로커 설정
      "sudo mv /home/ubuntu/server.properties ${var.kafka_ver}/config/server.properties",

      # 카프카 실행
      "${var.kafka_ver}/bin/kafka-server-start.sh -daemon ${var.kafka_ver}/config/server.properties",

      # 실행확인
      "jps -vm",

      # 카프카 정상동작 확인용 정보 요청 # terraform으로 실행시 broker id 가 -1로 인식되는 문제가 있음.
      #"${var.kafka_ver}/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092",
    ]
  }
}

