"""JDBC소스커넥터에서 timestampe모드 및 incrementing+timestamp 모드 테스트.

SQL Server 사용시 timestamp컬럼으로 DATETIME2를 사용해야 한다.
DATETIME 타입은 DATETIME2보다 정밀도가 떨어져 중복이슈가 있다.
DATETIME 타입은 Exception이 발생한다.

컬럼 이름의 대소문자를 바꾸면 DATETIME2 체크를 통과하는 버그가 있다.
이를 이용해 우회하여 DATETIME을 사용할 수 있다.
만약 원본 DB가 incrementing컬럼 등과 조합하여 개별 로그의 unique함을 보장해준다면, 우회 방법도 사용해볼만 해 보인다.


추가:
JsonConverter는 schema를 디폴트로 덧붙여서 저장한다.
딱히 필요없다면 가벼움을 위해 해당 옵션을 false로 저장해주자.
이렇게 저장하면 topic에도 순수 json만 남게되며, consumer단에서도 schema 없이 consume 해야 한다.

"""

import json
import requests

####################################
# 보안 주의. git push 주의
####################################
connect_ip = 'localhost:8083'

db_ip = '0.0.0.0:1433'
db_name = 'TutorialDB'
db_user = 'tester'
db_pass = 'tester^381'
db_table = 'Customers'
incrementing_col = 'CustomerId'
timestamp_col = 'regdate'  # 원본은 RegDate
####################################

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

query = f"""
SELECT * FROM  {db_table}
"""
# where CustomerId > 1

body = {
    "name": "jdbc-src-query-7",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",

        "tasks.max": "1",
        "connection.url": f"jdbc:sqlserver://{db_ip};databaseName={db_name}",
        "connection.user": db_user,
        "connection.password": db_pass,
        # "mode": "bulk",
        # "mode": "incrementing",
        # "mode": "timestamp",
        "mode": "timestamp+incrementing",
        "incrementing.column.name": incrementing_col,
        "timestamp.column.name": timestamp_col,
        # "timestamp.initial": -1,  # start from current time

        "topic.prefix": "test-jdbc-220928-3",

        "query": query,
        "db.timezone": "Asia/Seoul",

        # JsonConverter에서 스키마 미사용하기
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": False

    }
}

kafka_connect = f'http://{connect_ip}/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)  # NOQA
print(response)