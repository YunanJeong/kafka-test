## kafka-basic
- kafka 시작하기
- terraform 사용
- EC2 인스턴스 1개에 zookeeper, kafka 각각 하나씩 실행시킨다.
- 접속 후 `$jps -vm` 으로 각 프로세스 실행 유무 확인

## ami
- Ubuntu 22.04 LTS. 쌩 우분투. tfvars 파일로 변경가능
- instance_type: tfvars 파일로 설정

## config_example.tfvars.example
- `config.tfvars`로 이름 변경 후, 세부설정하고 사용한다.

## 실행
- 초기화: `$terraform init`
- 실행: `$terraform apply -var-file="./config/config.tfvars" -auto-approve`
- 종료: `$terraform destroy -var-file="./config/config.tfvars" -auto-approve`

## 버전
- Terraform: v1.2.1 on linux_amd64
- kafka binary 2.13
