# connect-offset-modifier

- 다수 커넥터에 대해 오프셋 변경하기
- 커넥터 수가 많을 경우 일정부분 자동화가 필요
- JDBC Source Connector는 "현재 시점 부터(latest)" 쿼리하기가 안됨
  - 이미 데이터가 많이 쌓인 테이블의 경우 처음부터 가져오므로 상당한 부하가 발생
  - `timestamp.initial=-1`이 있지만 제약사항이 많음.
  - DB timestamp컬럼이 규격에 맞지 않거나 존재하지 않으면 사용하기 힘듦
- id 기반으로 가져오고 있을때 모든 테이블 커넥션에 대해 MAX(id)값을 구한 후 이걸 connect-offset에 주입한다.

## 순서

## MAX(id) 가져오기
- connector config 정보 기반으로 모든 DB Table 커넥션 정보를 가져옴
- 해당 모든 커넥션에 대해 MAX(id) 값 구하기

## MAX(id)를 connect-offsets에 주입하기
- connector list 추출
- connect-offsets에서 현재 커넥터 이름과 매치되는 모든 key를 가져옴
- 해당 key의 value로 MAX(id)값 주입하기






```sh
# 전체 커넥터의 name과 특정config 추출
curl -s 'http://localhost:8083/connectors?expand=info' \
| jq -c '
  to_entries[]
  | {
      name: .key,
      connector_class: .value.info.config["connector.class"],
      connection_url:  .value.info.config["connection.url"],
      catalog_pattern: .value.info.config["catalog.pattern"]
    }
' > /tmp/connector-list

# JDBC Source Connector만 추출
cat /tmp/connector-list | grep "JdbcSourceConnector" 
```