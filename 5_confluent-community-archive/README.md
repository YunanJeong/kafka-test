# confluent-community-archive
- Confluent Platform Community 버전을  archive(zip or tar) 파일로 로컬 셋업하기

## 실행
- 초기화: `$terraform init`
- 실행: `$terraform apply -var-file="./config/config.tfvars" -auto-approve`
- 종료: `$terraform destroy -var-file="./config/config.tfvars" -auto-approve`

## 기타
