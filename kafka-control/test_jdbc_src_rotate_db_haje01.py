"""DB가 하루마다 로테이션 될 때 테스트.

- https://github.com/haje01/kafka-connect-jdbc 의 수정된 커넥터 사용
- 이 커넥터는 현재 bulk모드를 지원하지 않는다
- 이 커넥터는 query 옵션을 반드시 사용해야한다.
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
####################################

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# haje01/kafka-connect-jdbc에서 query 문으로 DB 로테이션에 대응한다.
query = f"""
SELECT * FROM
(
    SELECT * FROM {db_table}_{{{{ DayAddFmt -1 yyMMdd }}}}
    UNION ALL
    SELECT * FROM {db_table}
) AS T
-----
SELECT * FROM {db_table}
"""

print(query)
body = {
    "name": "jdbc-src-haje",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",

        "tasks.max": "3",
        "connection.url": f"jdbc:sqlserver://{db_ip};databaseName={db_name}",
        "connection.user": db_user,
        "connection.password": db_pass,
        # 이 커넥터는 현재 bulk모드를 지원하지 않는다.
        "mode": "incrementing",
        "incrementing.column.name": incrementing_col,
        "topic.prefix": "test-jdbc-220927-",
        "db.timezone": "Asia/Seoul",
        "query": query,
    }
}

kafka_connect = f'http://{connect_ip}/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)  # NOQA
print(response)