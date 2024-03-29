# kafka-jdbc-connector-test
- terraform으로 하나의 EC2 인스턴스에서 kafka broker, connect, jdbc source connector를 실행시키는 예제
- 오픈소스 커넥터인 jdbc 커넥터 사용시 메모, 참고사항 등

## 실행
- 초기화: `$terraform init`
- 실행: `$terraform apply -var-file="./config/config.tfvars" -auto-approve`
- 종료: `$terraform destroy -var-file="./config/config.tfvars" -auto-approve`

## 이슈
- 로컬 DB로 테스트하는 경우, EC2에서 로컬PC의 IP로 접근하지 못할 수 있다.
	- 이 경우, [EC2 DB 인스턴스 생성](https://github.com/YunanJeong/terraform-test) 후 다음 명령어로 ip를 별도 설정하여 테스트할 수 있다.
		- `$terraform apply -var-file="./config/config.tfvars" -var="db_ip={DB instance ip}"`
## 파일
-  커넥트를 standalone 모드로 실행시: `config/jdbc-src-connector-settings.properties`
	- jdbc 소스 커넥터용 설정파일 백업(ms sqlserver에 연결했던 것. 민감정보 지움)
	- 커넥트 실행시 함께 참조해주는 파일이다.

<br/>

- 커넥트를 distributed 모드로 실행시: `config/jdbc-src-connector-settings.json`
	- distributed모드 커넥트에서 jdbc 소스커넥터를 생성할 때 RESTapi의 body로 넣을 json 내용이다.
	- 이 파일을 사용하여 커넥터 생성은 다음과 같이 할 수 있다.
		- `$curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @./config/jdbc-src-connector-settings.json`
		- localhost는 예시이고, 커넥트의 ip를 가리켜야 한다.
		- 보통은 curl보다 python requests로 많이들 처리하는 듯 하다.

	- properties파일을 json으로 변환 후, "name"외에 key-value를 모두 "config"키로 옮긴 것이다. 사실상 내용은 위 properties와 동일하다.
	- confluent cli를 사용하면 properties 파일을 그대로 활용하여 distributed 모드에서도 커넥터 생성이 가능하다.
		- 하지만, confluent cloud or platform을 사용하지 않는다면 confluent cli 활용도가 떨어지므로 그냥 필요한 속성파일들을 json으로 만들어두는게 나을 듯 싶다.

