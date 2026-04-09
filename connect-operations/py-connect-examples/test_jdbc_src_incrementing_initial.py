"""incrementing_initial 테스트.
- incrementing 모드 첫 실행시 가져올 첫 행을 지정하는 방법
  - 서브쿼리의 where 절로 조건을 걸 수 있다.
  - offset을 수동 지정해도 되지만, 다소 번거롭다.
  - TIP) query 대신 whitelist 모드로만 가져오는 경우,
    - 커넥터 최초 실행시는 query모드로 일부 로그를 가져온 후,
    - offset이 신규등록되면 whitelist모드로 옵션을 수정하면 된다.
- incrementing 모드는 원래 첫실행시 테이블의 모든 행을 가져오도록 되어있다.
- bulk모드 외에는 where절을 바로 사용할 수 없다.

"""
import json
import requests

####################################
# 보안 주의. git push 주의
####################################
connect_ip = 'localhost:8083'

db_ip = 'localhost:1433'
db_name = 'TutorialDB'
db_user = 'tester'
db_pass = 'tester^381'
db_table = 'Customers'
incrementing_col = 'CustomerId'
incrementing_initial = "RegDate > CONVERT(DATETIME, '2022-05-11 00:00:01.000')"
####################################

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

query = f"""
select *from
(
select * from {db_table}
where {incrementing_initial}
)AS T

"""

body = {
    "name": "jdbc-src13",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",

        "tasks.max": "1",
        "connection.url": f"jdbc:sqlserver://{db_ip};databaseName={db_name}",
        "connection.user": db_user,
        "connection.password": db_pass,
        "mode": "incrementing",
        "incrementing.column.name": incrementing_col,
        "topic.prefix": "test-221011-13",

        "query": query,
        "db.timezone": "Asia/Seoul",

        # JsonConverter에서 스키마 미사용하기
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": False
    }
}

# ensure_ascil 옵션: 한글 등을 아스키가 아니라 한글 그대로 보여줌
kafka_connect = 'http://'+connect_ip+'/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)
print(response)