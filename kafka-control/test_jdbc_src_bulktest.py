"""Bulk 모드 테스트.

- bulk모드에서 query 옵션사용시 where절 사용가능하다.
- bulk모드에서 query 옵션과 whitelist, blacklist는 같이 사용할 수 없다.(테이블 지정 중첩되므로)

- whitelist로 다수 테이블을 동시에 bulk로 수집시, DB명과 view명을 일반적으로 다써줘야 한다.
    => 아래 db_tables 변수 참고
- 안쓰면 기본DB명, dbo가 붙지만, 실제 다양한 view를 제공하는 라이브DB에서는 오류가 발생할 수 있다.

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
timestamp_col = 'regdate'
incrementing_initial = "RegDate > CONVERT(DATETIME, '2022-05-11 00:00:01.000')"
####################################

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


db_tables = ['TutorialDB.dbo.Customers', 'TutorialDB.dbo.Customers2', ]
body = {
    "name": "jdbc-src-7",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",

        "tasks.max": "11",
        "connection.url": f"jdbc:sqlserver://{db_ip};databaseName={db_name}",
        "connection.user": db_user,
        "connection.password": db_pass,
        "mode": "bulk",
        "topic.prefix": "test-221019-7",

        # "query": query,
        "db.timezone": "Asia/Seoul",
        "table.whitelist": ','.join(db_tables),  # 특정 테이블들만 조회
        # "table.blacklist": "xxx",  # 특정 테이블 제외

        # JsonConverter에서 스키마 미사용하기
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": False,

        "poll.interval.ms": 1500000,  # default: 5000ms
        # "batch.max.rows": 1000,  # default: 100개  # 벌크모드에서는 작동 X
        "timestamp.delay.interval.ms": 2000,  # default: 0ms

    }
}



# ensure_ascil 옵션: 한글 등을 아스키가 아니라 한글 그대로 보여줌
kafka_connect = 'http://'+connect_ip+'/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)
print(response)