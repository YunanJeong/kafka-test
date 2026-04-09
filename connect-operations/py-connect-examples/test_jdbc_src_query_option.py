"""쿼리 옵션 테스트.

# bulk mode 일 때만 query문에 where절을 넣을 수 있다.
# query 옵션을 쓰면 whitelist, blacklist 옵션은 쓸 수 없다.
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
SELECT *
, DATENAME(YEAR, RegDate)                                       AS [year]
, right( '0' + CONVERT(NVARCHAR, DATEPART(MONTH, RegDate)), 2 ) AS [month]
, right( '0' + DATENAME(DAY, RegDate),                      2 ) AS [day]
, right( '0' + DATENAME(HOUR, RegDate),                     2 ) AS [hour]
FROM {db_table}
WHERE CustomerId > 1
"""

body = {
    "name": "jdbc-src-query",
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