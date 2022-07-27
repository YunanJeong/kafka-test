# kafka-jdbc-connector-test
오픈소스 커넥터인 jdbc 커넥터 사용시 메모, 참고사항

## 파일
- jdbc-src-connector-settings.properties
	- jdbc 소스 커넥터용 설정파일 백업(ms sqlserver에 연결했던 것. 민감정보 지움)
	- standalone모드 커넥트 실행시 함께 참조해주는 파일이다.

- jdbc-src-connector-settings.json
	- distributed모드 커넥트에서 jdbc 소스커넥터를 생성할 때 RESTapi의 body로 넣을 데이터파일이다.
	- 이 파일을 사용하여 커넥터 등록은 다음과 같이 할 수 있다.
		- `$curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @./config/jdbc-src-connector-settings.json`
		- localhost는 예시이고, 커넥트의 ip를 가리켜야 한다.

	- properties파일을 json으로 변환 후, "name"외에 key-value를 모두 "config"키로 옮긴 것이다. 사실상 내용은 위 properties와 동일하다.
	- confluent cli를 사용하면 properties 파일을 그대로 활용하여 distributed 모드에서도 커넥터 생성이 가능하다.
		- 하지만, confluent cloud or platform을 사용하지 않는다면 confluent cli 활용도가 떨어지므로 그냥 필요한 속성파일들을 json으로 만들어두는게 나을 듯 싶다.
