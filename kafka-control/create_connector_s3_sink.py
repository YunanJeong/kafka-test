"""s3-sink 사용시, AWS Credential 필요.

guava.jar 별도 다운로드 후 플러그인 경로에 설치 필요.
"""
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

# "store.kafka.keys": "true",  # default: false. # record의 key를 별도파일로 저장하기. true인데 record의 key가 null이면 에러 발생.
# "keys.format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat", 별도 저장할 key의 파일 형식

# ensure_ascil 옵션: 한글 등을 아스키가 아니라 한글 그대로 보여줌
kafka_connect = 'http://localhost:8083/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)
print(response)