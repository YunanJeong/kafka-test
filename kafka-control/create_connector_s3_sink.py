import json
import requests

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

body = {
    "name": "my-connector-name",
    "config": {
        "topics": "my-topic-name",
        "tasks.max": 3,
        "connector.class": "io.confluent.connect.s3.S3SinkConnector",
        # "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
        "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
        "storage.class": "io.confluent.connect.s3.storage.S3Storage",
        "flush.size": 1000,
        "s3.bucket.name": "my-s3-bucket-name",
        "s3.region": "ap-northeast-2",
        "topics.dir": "my-s3-dir",
        # "s3.compression.type": "gzip",
        "s3.compression.type": "none",
        "locale": "ko_KR",
        "timezone": "Asia/Seoul"
    }
}

# ensure_ascil 옵션: 한글 등을 아스키가 아니라 한글 그대로 보여줌
kafka_connect = 'http://localhost:8083/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)
print(response)