"""커넥터 여러개 붙이기 테스트.

# 여러 테이블에 대해 각각 커넥터를 설정해서 별도 관리할 때 필요하다.
# 40개쯤 돌려봤는데 DB서버, Kafka 서버에 둘다 부담되지 않는다.
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

query = f"""
SELECT * FROM  {db_table}
where CustomerId > 3
"""

for number in range(0, 40):
    body = {
        "name": f"jdbc-src-query+{number}",
        "config": {
            "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",

            "tasks.max": "1",
            "connection.url": f"jdbc:sqlserver://{db_ip};databaseName={db_name}",
            "connection.user": db_user,
            "connection.password": db_pass,
            "mode": "bulk",
            # "mode": "incrementing",
            # "incrementing.column.name": incrementing_col,
            "topic.prefix": "test-jdbc2-",

            # 사용 불가
            # "table.whitelist": db_table,  # 특정 테이블들만 조회
            # "table.blacklist": "xxx",  # 특정 테이블 제외

            "query": query,

        }
    }

    kafka_connect = 'http://'+connect_ip+'/connectors'
    response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)  # NOQA
    print(response)