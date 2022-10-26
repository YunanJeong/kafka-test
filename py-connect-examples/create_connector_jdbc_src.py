import json
import requests

####################################
# 보안 주의. git push 주의
####################################
connect_ip = '0.0.0.0:8083'

db_ip = '0.0.0.0:1433'
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

body = {
    "name": "jdbc-src",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
        "tasks.max": "1",
        "connection.url": "jdbc:sqlserver://"+db_ip+";databaseName="+db_name,
        "connection.user": db_user,
        "connection.password": db_pass,
        #"mode": "bulk",
        "mode": "incrementing",
        "incrementing.column.name": incrementing_col,
        "topic.prefix": "test-jdbc-"
    }
}

    #"table.whitelist": "Customers, table1, table2", # 특정 테이블들만 조회
    #"table.blacklist": "xxx",  # 특정 테이블 제외

    # 특정 값을 record의 key로 취급하여 토픽에 저장하기. whitelist 설정 필요.
    #"transforms": "createKey,extractInt",
    #"transforms.createKey.type": "org.apache.kafka.connect.transforms.ValueToKey",
    #"transforms.createKey.fields": "CustomerId",
    #"transforms.extractInt.type": "org.apache.kafka.connect.transforms.ExtractField$Key",
    #"transforms.extractInt.field": "CustomerId",

# ensure_ascil 옵션: 한글 등을 아스키가 아니라 한글 그대로 보여줌
kafka_connect = 'http://'+connect_ip+'/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)
print(response)