"""s3-sink 사용시, AWS Credential 필요.

FieldPartitioner 테스트
"""

import json
import requests

####################################
# 보안 주의. git push 주의
####################################
connect_ip = 'localhost:8083'
####################################
s3_region = 'ap-northeast-2'
s3_bucket = 'my-bucket'
####################################
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

body = {
    "name": "s3-sink",
    "config": {
        "topics": "test-jdbc-220921-",  # "test-jdbc-Customers"
        "tasks.max": 3,
        "connector.class": "io.confluent.connect.s3.S3SinkConnector",
        "storage.class": "io.confluent.connect.s3.storage.S3Storage",
        "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
        "partitioner.class": "io.confluent.connect.storage.partitioner.FieldPartitioner",  # NOQA
        "partition.field.name": "Name, CustomerId",

        "flush.size": 10,

        "s3.region": s3_region,
        "s3.bucket.name": s3_bucket,
        "topics.dir": "yunantest",  # default: topics/

    }
}

kafka_connect = 'http://'+connect_ip+'/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)
print(response)