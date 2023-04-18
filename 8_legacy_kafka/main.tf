######################################################################
# Set Up Instance
######################################################################
module "ubuntu" {
    source = "./modules/ec2/ubuntu"
    # Module's Variables Assignment
    ami              = var.ami
    instance_type    = var.instance_type
    tags             = merge(var.tags, {Name = var.tag_name}, )
    key_name         = var.key_pair_name
    private_key_path = var.private_key_path
    work_cidr_blocks = var.my_ip_list
}

######################################################################
# 보안그룹 추가
######################################################################
resource "aws_security_group" "kafka_sgroup"{
  name = "yunan_kafka_sgroup_${var.tag_name}"
  ingress {
    from_port = 9092
    to_port = 9092
    description = "for kafka broker"
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
    from_port = 2181
    to_port = 2181
    description = "for kafka zookeeper"
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
# 보안그룹을 인스턴스에 등록
module "register_sgroup" {
    source = "./modules/sgroup/register_sgroup"
    # Module's Variables
    sgroup_id        = aws_security_group.kafka_sgroup.id
    instance_id_list = ["${module.ubuntu.id}"]
}

data "template_file" "kafka_properties" {
  template = file("${path.module}/config/server.properties")
  vars = {
    AWS-PUBLIC-DNS-OR-HOSTNAME-HERE = module.ubuntu.public_dns
  }
}

#################################################
# Ubuntu Commands
#################################################
resource "null_resource" "ubuntu_remote"{

  # remote-exec를 위한 ssh connection 셋업
  connection {
    type = "ssh"
    host = module.ubuntu.public_ip
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

  # 실행된 원격 인스턴스에서 수행할 cli명령어
  provisioner "remote-exec" {
    inline = [
      "cloud-init status --wait",
      "sudo apt update ; sudo apt install -y openjdk-8-jdk-headless",

      # Kafka 설치
      "wget https://archive.apache.org/dist/kafka/0.9.0.0/kafka_2.11-0.9.0.0.tgz",
      "sudo tar xzf kafka_*.tgz",
      "sudo mv ~/kafka_*/ /kafka/", 
      "sudo mv ~/config/*.properties /kafka/config/",

      # 서비스등록 (zookeeper, broker)
      "sudo mv ~/config/*.service /lib/systemd/system/",
      "sudo systemctl daemon-reload",
      "sudo systemctl restart broker.service",  # zookeeper는 broker의 requires로 실행
    ]
  }
}

