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
  ingress {
    from_port = 8083
    to_port = 8083
    description = "for kafka connect"
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

  provisioner "file" {
    content = data.template_file.kafka_properties.rendered
    destination = "/home/ubuntu/server.properties"
  }
  provisioner "file"{
    content = file("${path.module}/config/connect-distributed.properties")
    destination = "/home/ubuntu/connect-distributed.properties"
  }

  provisioner "file"{
    content = file("${path.module}/config/zookeeper.service")
    destination = "/home/ubuntu/zookeeper.service"
  }
  provisioner "file"{
    content = file("${path.module}/config/broker.service")
    destination = "/home/ubuntu/broker.service"
  }
  provisioner "file"{
    content = data.template_file.connect_service.rendered
    destination = "/home/ubuntu/connect.service"
  }
  # 실행된 원격 인스턴스에서 수행할 cli명령어
  provisioner "remote-exec" {
    inline = [
      "cloud-init status --wait",
      "sudo apt update ; sudo apt install -y openjdk-8-jdk-headless",

      "wget ${var.kafka_index}",
      "tar xvf ${var.kafka_ver}.tgz",
      "sudo mv ${var.kafka_ver} /usr/local/kafka",  # 디렉토리 이름을 변경하면서 이동

      # 브로커 설정(서비스 실행시 bash파일등의 환경변수 안먹히니, 서비스 파일에서 지정)
      "sudo mv ~/server.properties /usr/local/kafka/config/server.properties",

      # 커넥트 설정
      "sudo mv ~/connect-distributed.properties /usr/local/kafka/config/connect-distributed.properties",

      # 필요 커넥터 설치
      "wget ${var.jdbc_con_index} ${var.s3_con_index}",
      "sudo apt install unzip  &&  unzip '~/*.zip'",
      "sudo mkdir -p /usr/local/share/kafka/plugins",
      "sudo mv ~/${var.jdbc_con_ver}  /usr/local/share/kafka/plugins/",
      "sudo mv ~/${var.s3_con_ver}  /usr/local/share/kafka/plugins/",

      # s3 커넥터 관련 추가 셋업
      "wget https://repo1.maven.org/maven2/com/google/guava/guava/11.0.2/guava-11.0.2.jar",
      "sudo mv ~/guava-11.0.2.jar /usr/local/share/kafka/plugins/${var.s3_con_ver}/lib/",

      # 서비스등록
      "sudo mv ~/zookeeper.service /etc/systemd/system/",
      "sudo mv ~/broker.service /etc/systemd/system/",
      "sudo mv ~/connect.service /etc/systemd/system/",
      "sudo systemctl daemon-reload",
      "sudo systemctl start broker.service connect.service",  # zookeeper는 broker의 requires로 실행

      # 실행확인 # remote-exec의 마지막이 데몬실행이면 무시된다. 바로 뒤에 간단한 커맨드나 아주 짧은 지연이라도 있어야 무시되지 않는다.
      "jps -vm",



      # 카프카 정상동작 확인용 정보 요청 # terraform으로 실행시 broker id 가 -1로 인식되는 문제가 있음.
      #"${var.kafka_ver}/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092",
      # 토픽 리스트 확인
      # ./bin/kafka-topics.sh --list --bootstrap-server localhost:9092,
      # 토픽 데이터 확인
      # ./bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic {토픽명} --from-beginning
    ]
  }
}

