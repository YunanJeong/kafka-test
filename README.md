# kafka-test
kafka-test

## 디렉토리
```
├── 0_kafka-broker-basic            # Set up kafka 1 node (zookeeper, broker) by Apache Kafka
├── 1_kafka-broker-connect-basic    # Add kafka connect to "module 0"
├── 2_kafka-broker-connect-systemd  # Run "module 1"'s kafka as systemd service
├── 3_kafka-jdbc-connector-test     # Add connectors(jdbc-src, s3-sink) to "module 2"
├── 4_kafka-ksql-service            # Add ksqlDB to "module 3"
├── 5_confluent-community-archive   # Set up kafka 1 node by Confluent Platform Community(zip or tar)
├── 6_confluent-community-package   # Set up kafka 1 node by Confluent Platform Community(deb)
├── LICENSE
├── README.md
├── basic-instance
├── memo
├── py-connect-examples             # Test connectors
├── py-connect-util                 # Simple library to manage connectors
├── py-kafka-packages
└── test-db-broker-s3
```

## Record - Kafka Message Structure
Kafka의 가장 작은 메시지 단위를 Record라고 부른다.
Record = Message = Event = Data = log 1 row 이라고 보면 된다.
- [참고 그림](https://www.google.com/search?q=kafka+record+timestapme&tbm=isch&ved=2ahUKEwib6f2Lm4L6AhXPZ94KHWiqBJ0Q2-cCegQIABAA&oq=kafka+record+timestapme&gs_lcp=CgNpbWcQAzoECCMQJzoECAAQEzoGCAAQHhATOgUIABCABDoECAAQHjoECAAQGFDQB1iRKWD3LWgAcAB4AIABcYgB_BqSAQUxNC4yMJgBAKABAaoBC2d3cy13aXotaW1nwAEB&sclient=img&ei=ZU8YY9uiIs_P-Qbo1JLoCQ&bih=969&biw=1920&rlz=1C1GCEA_enKR959KR967#imgrc=0ffhDAgddKBNRM)

### Header
	- 메타데이터(topic, patition, timestamp(Ingestion Time) 정보 등)
	- 시스템 입장에서 Record를 분류하기 위한 정보가 자동 기록됨
### Body(Business Relevant Data)
	- 원본 데이터, Payload에 해당한다.
	- key
		- 개발&운영자 입장에서 Record를 분류하기 위한 정보
	- value
		- 핵심 Payload, 원본데이터에 가까움


## 설치
- [라이센스 자세한 정리](https://github.com/YunanJeong/kafka-test/blob/main/memo/memo_kafka_license.md)
- [설치방법 및 관련 라이센스](https://github.com/YunanJeong/kafka-test/blob/main/memo/memo_kafka_install.md)

## How to Analyze and Manage Kafka Messages
- [kafkacat과 jq, 기타 필수 쉘 명령어 사용법](https://github.com/YunanJeong/kafka-test/blob/main/memo/memo_kafkacat_and_jq.md)
