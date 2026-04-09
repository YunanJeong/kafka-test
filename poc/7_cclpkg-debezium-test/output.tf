# $terraform apply 후, 아래 내용에 해당하는 정보가 stdout으로 출력된다.
# 여기서는 인스턴스 ID와 IP 예시이다.
# infra가 실행중instance일 떄, $terraform output으로도 조회가능하다.
# output들은 현재 infra나 다른 terraform 프로젝트에서 사용가능하다.

######################################################################
# Instance Information
######################################################################
output "id" {
  description = "ID of the EC2 instance"
  value       = module.ubuntu.id
}
output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = module.ubuntu.public_ip
}
output "tags" {
  description = "Instance Tags"
  value = module.ubuntu.tags
}

output "public_dns"{
  value       = module.ubuntu.public_dns
}
output "public_hostname_in_ec2"{
  value = split(".", module.ubuntu.public_dns)[0]
}
output "private_dns" {
  value = module.ubuntu.private_dns
}
output "hostname" {
  description = "hostname"
  value = split(".", module.ubuntu.private_dns)[0]
}
output "instance_type" {
  value = module.ubuntu.instance_type
}


output "sqlserver_id" {
  value       = module.sqlserver.id
}
output "sqlserver_public_ip" {
  value       = module.sqlserver.public_ip
}
output "sqlserver_tags" {
  value = module.sqlserver.tags
}