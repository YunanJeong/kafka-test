variable "key_pair_name"{
  type = string
  default = "key_pair_name"
}
variable "private_key_path"{
  type = string
  default = "Directory of key_pair_file(pem)"
}
variable "tags"{
  description = "instance tags"
  type = map(string)
  default = ({
    Owner = "xxxxx@gmail.com"
    Service = "tag-Service"
  })
}
variable "my_ip_list"{
  description = "ssh 접속용 보안그룹 생성을 위한 내 pc의 public ip 목록"
  type = list(string)
}
######################################################################
# Set Up Basic
######################################################################
variable "ami_fluentd"{}
variable "tag_name_fluentd"{}
variable "instance_type_fluentd"{
  default = "t2.micro"
}

######################################################################
#Set Up Existing Git Server
######################################################################
variable "git_info"{
  type = map(string)
  default = ({
    user = "yunan"
    token = ""
  })
}
variable "gitlab_instance"{
  default = ""
}

