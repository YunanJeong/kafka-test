"""Timezone 테스트.

# db.timezone과 locale 옵션
    => TimeBasedPartitioner와 함께 사용된다. s3 상에서 디렉토리 분류 기준이 된다.
# db.timezone (Eventtime을 그대로 가져오는 RecordField 옵션 사용을 기준으로 다음과 같이 동작한다.)
    - 대상 Kafka topic record에 기입된 EventTime을 timezone에 맞게 해석하여 디렉토리를 분류한다.
    - e.g.) Eventtime이 'UTC 2023년 1월 16일 15시 0분 0초'에 해당하는 timestamp가 있다고 하자.
        - db.timezone="Asia/Seoul"이면 KST 시간인 '2023년 1월 17일 0시 0분 0초'로 해석하여 s3 파티셔닝이 수행된다.

# locale
    => locale은 일반적으로 "UI에서 사용되는 언어, 지역 설정, 출력 형식 등을 정의하는 문자열"을 의미한다.
    => confluent document에는 TimeBasedPartitioner와 함께 date및 time 에 관여한다고 되어있다.
    => 다만 이는 timezone과는 무관하다.
    => 또한, timestamp으로 시간을 다룰 때는 별 의미가 없어 보인다.
    => 또한, path.format으로 디테일하게 연월일 순을 지정해버려도 별 의미가 없는 옵션일 듯 하다.
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
        "connector.class": "io.confluent.connect.s3.S3SinkConnector",
        "storage.class": "io.confluent.connect.s3.storage.S3Storage",
        "format.class": "io.confluent.connect.s3.format.json.JsonFormat",

        # "topics": "topic1, topic2, topic3, ...",
        "s3.region": s3_region,
        "s3.bucket.name": s3_bucket,
        "topics.dir": "utc_s3_test",
        "s3.compression.type": "gzip",

        "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",  # NOQA
        "path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",
        "partition.duration.ms": "3600000",  # hourly   # "86400000",       # Daily S3 Partition
        "locale": "ko_KR",
        "timezone": "Asia/Seoul",
        "timestamp.extractor": "RecordField",      # Event Time 기준 S3 Partition
        # "timestamp.field": "",

        "rotate.schedule.interval.ms": "600000",  # 10분마다 새 파일 업로드
        "flush.size": 100000,

        # JsonConverter에서 스키마 미사용하기
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": False,


        "topics": "jdbc-timezonetestCustomers",
        "tasks.max": 1,                            # 한 토픽의 파티션 수 만큼 지정(토픽 수 아님)
        "timestamp.field": "RegDate",
    }
}

kafka_connect = 'http://'+connect_ip+'/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)
print(response)