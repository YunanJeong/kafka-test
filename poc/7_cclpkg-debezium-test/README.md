# cclpkg-debezium-test
- cclpkg: Confluent Community License 버전을  Debian(Ubuntu) 패키지 파일로 로컬 셋업
- debezium(SQL Server) 소스 커넥터 테스트 용도

## 실행
- 초기화: `$terraform init`
- 실행: `$terraform apply -var-file="./config/config.tfvars" -auto-approve`
- 종료: `$terraform destroy -var-file="./config/config.tfvars" -auto-approve`

## 기타
