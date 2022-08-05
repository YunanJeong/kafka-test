# kafka-broker-connect-basic
- terraform으로 하나의 EC2 인스턴스에서 kafka broker, connect를 실행시키는 예제
- connect는 distritubed mode이다. 커넥터 생성,삭제, 조회 등은 connect REST api 를 참조한다.

## 실행
- 초기화: `$terraform init`
- 실행: `$terraform apply -var-file="./config/config.tfvars" -auto-approve`
- 종료: `$terraform destroy -var-file="./config/config.tfvars" -auto-approve`

## 기타
