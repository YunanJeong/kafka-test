# confluent-community-archive
- Confluent Platform Community 버전을 아카이브파일(zip or tar)로 로컬셋업하기

## 실행
- 초기화: `$terraform init`
- 실행: `$terraform apply -var-file="./config/config.tfvars" -auto-approve`
- 종료: `$terraform destroy -var-file="./config/config.tfvars" -auto-approve`

## 기타
