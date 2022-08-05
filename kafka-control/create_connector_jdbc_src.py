import json
import requests

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

body = {
    "name": "test-source-sqlite-jdbc-autoincrement",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
        "tasks.max": "1",
        "connection.url": "jdbc:sqlserver://${SET-DB-IP-HERE};databaseName=${SET-DB-NAME-HERE}",
        "connection.user": "${SET-DB-USER-HERE}",
        "connection.password": "${SET-DB-PASS-HERE}",
        "mode": "bulk",
        "incrementing.column.name": "${SET-DB-TABLENAME-HERE}",
        "topic.prefix": "test-jdbc-"
    }
}

# ensure_ascil 옵션: 한글 등을 아스키가 아니라 한글 그대로 보여줌
kafka_connect = 'http://localhost:8083/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)
print(response)