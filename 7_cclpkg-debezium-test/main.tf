######################################################################
# Set Up Instance
######################################################################

module "sqlserver" {
    source = "./modules/ec2/sqlserver"
    # Module's Variables
    ami              = var.mssql_ami
    instance_type    = var.mssql_instance_type
    tags             = var.mssql_tags

    db_user = var.mssql_db_user
    db_pass = var.mssql_db_pass
    db_port = var.mssql_db_port

    key_name         = var.key_pair_name
    private_key_path = var.private_key_path
    work_cidr_blocks = var.my_ip_list
}

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

data "template_file" "kafka_properties" {
  template = file("${path.module}/config/server.properties")
  vars = {
    AWS-PUBLIC-DNS-OR-HOSTNAME-HERE = module.ubuntu.public_dns
  }
}
data "template_file" "connect_service" {
  template = file("${path.module}/config/connect.service")
  vars = {
    AWS-ACCESS-KEY-HERE = var.aws_access_key
    AWS-SECRET-KEY-HERE = var.aws_secret_key
  }
}
data "template_file" "test_db_info"{
  template = file("${path.module}/config/test_db_info.json")
  vars = {
    PUBLIC-IP = module.sqlserver.public_ip
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
  provisioner "file"{
    content = data.template_file.connect_service.rendered
    destination = "/home/ubuntu/config/connect.service"
  }
  provisioner "file"{
    content = data.template_file.test_db_info.rendered
    destination = "/home/ubuntu/config/test_db_info.json"
  }

  # 실행된 원격 인스턴스에서 수행할 cli명령어
  provisioner "remote-exec" {
    inline = [
      "cloud-init status --wait",
      "sudo apt update ; sudo apt install -y openjdk-11-jdk-headless",

      # Kafka 설치
      "chmod +x ~/config/install_confluent_community.sh",
      "sudo ~/config/install_confluent_community.sh",
      "sudo mv ~/config/*.properties /etc/kafka/",

      # 필요 커넥터 설치
      "sudo mkdir -p /opt/connectors",
      "cd /opt/connectors",
      "sudo wget ${var.debezium_con_index} ${var.jdbc_con_index} ${var.s3_con_index}",
      "sudo apt install unzip  &&  sudo unzip '*.zip'",
      "sudo tar -xvf *.tar.gz",
      "cd ~/",

      # 서비스등록 (zookeeper, broker, connect, ksqldb)
      "sudo mv ~/config/*.service /lib/systemd/system/",
      "sudo systemctl daemon-reload",
      "sudo systemctl restart broker.service connect.service ksqldb.service",  # zookeeper는 broker의 requires로 실행

      "sudo apt install python-is-python3",
      "git clone https://github.com/YunanJeong/kafka-connect-manager.git",
      "sudo cp ~/config/test_db_info.json ~/kafka-connect-manager/config/debezium_src/",
      "sudo chmod +x ~/config/install_docker.sh && sudo ~/config/install_docker.sh",

      # kafkacat
      "sudo docker pull confluentinc/cp-kafkacat",
      "echo \"alias kcat='sudo docker run --tty --network host confluentinc/cp-kafkacat kafkacat'\" >> ~/.bashrc"
    ]
  }
}

