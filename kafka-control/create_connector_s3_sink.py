"""s3-sink 사용시, AWS Credential 필요.

guava.jar 별도 다운로드 후 플러그인 경로에 설치 필요. => 10.1.1부터 필요없음. 버그패치됨.
"""

import json
import requests

####################################
# 보안 주의. git push 주의
####################################
connect_ip = 'localhost'
####################################

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

body = {
    "name": "s3-sink",
    "config": {
        "topics": "test-jdbc-Customers",
        "tasks.max": 1,
        "connector.class": "io.confluent.connect.s3.S3SinkConnector",
        "storage.class": "io.confluent.connect.s3.storage.S3Storage",
        "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
        "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
        # "partitioner.class": "io.confluent.connect.storage.partitioner.HourlyPartitioner",
        "path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",
        "partition.duration.ms": "3600000",

        "flush.size": 1,
        "rotate.interval.ms": "3600000",
        # => 만약 flush.size가 무한히 크고 데이터가 계속 들어온다고 가정하면,
        # => 이 설정이 없으면 몇시간이 지나도 다음 시간 파티션으로 넘어가지 않고, 한 파일에 계속 쓰고 있을 것이다.

        "s3.region": "ap-northeast-2",
        "s3.bucket.name": "wzdat-seoul",
        "topics.dir": "yunantest",

        "locale": "ko_KR",
        "timezone": "Asia/Seoul",
        "timestamp.extractor": "RecordField",
        "timestamp.field": "RegDate"
    }
}
#"partition.duration.ms"는 새 "path.format"을 생성하는 빈도를 결정하는 수치다.
# "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
# "store.kafka.keys": "true",  # default: false. # record의 key를 별도파일로 저장하기. true인데 record의 key가 null이면 에러 발생.
# "keys.format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat", 별도 저장할 key의 파일 형식

# "parquet.codec": "none",  # ParquetFormat과 세트. s3.compression.type과 역할이 비슷
# "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
# "s3.compression.type": "gzip",
# "timestamp.extractor"
    # "WallClock": Processing Time. 데이터 파이프라인의 최종앱에서 처리된 시스템 시간.(이 경우 sink connector가 처리한 시간)
    # "Record": Ingestion Time에 가까움. Record의 Headers(메타데이터)에 있는 timestamp (즉, kafka 토픽에 적재된 시간)
    # "RecordField": Event Time. 원본로그의 시간. "timestamp.field항목을 추가로 써서 record의 특정 시간 필드를 지정할 수 있음
    # 각 시간옵션: https://developer.confluent.io/patterns/stream-processing/wallclock-time/

# ensure_ascil 옵션: 한글 등을 아스키가 아니라 한글 그대로 보여줌
kafka_connect = 'http://'+connect_ip+':8083/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)
print(response)