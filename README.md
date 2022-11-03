# kafka-test
kafka-test

## 디렉토리
```
├── 0_kafka-broker-basic
├── 1_kafka-broker-connect-basic
├── 2_kafka-broker-connect-systemd
├── 3_kafka-jdbc-connector-test
├── 4_kafka-ksql-service
├── 5_confluent-community-archive
├── 6_confluent-community-package
├── LICENSE
├── README.md
├── basic-instance
├── memo
├── py-connect-examples
├── py-connect-util
├── py-kafka-packages
└── test-db-broker-s3
```

## Record - Kafka Message Structure
Kafka의 가장 작은 메시지 단위를 Record라고 부른다.
Record = Message = Event = Data = log 1줄 이라고 보면 된다.

### Record
- Header
	- 메타데이터(topic, patition, timestamp(Ingestion Time) 정보 등)
	- 시스템 입장에서 Record를 분류하기 위한 정보가 자동 기록됨
- Body(Business Relevant Data)
	- 원본 데이터, Payload에 해당한다.
	- key
		- 개발&운영자 입장에서 Record를 분류하기 위한 정보
	- value
		- 핵심 Payload, 원본데이터에 가까움

- [참고 그림](https://www.google.com/search?q=kafka+record+timestapme&tbm=isch&ved=2ahUKEwib6f2Lm4L6AhXPZ94KHWiqBJ0Q2-cCegQIABAA&oq=kafka+record+timestapme&gs_lcp=CgNpbWcQAzoECCMQJzoECAAQEzoGCAAQHhATOgUIABCABDoECAAQHjoECAAQGFDQB1iRKWD3LWgAcAB4AIABcYgB_BqSAQUxNC4yMJgBAKABAaoBC2d3cy13aXotaW1nwAEB&sclient=img&ei=ZU8YY9uiIs_P-Qbo1JLoCQ&bih=969&biw=1920&rlz=1C1GCEA_enKR959KR967#imgrc=0ffhDAgddKBNRM)


## 설치
- [라이센스 자세한 정리](https://github.com/YunanJeong/kafka-test/blob/main/memo/memo_kafka_license.md)
- [설치방법 및 관련 라이센스](https://github.com/YunanJeong/kafka-test/blob/main/memo/memo_kafka_install.md)

## How to Analyze and Manage Kafka Messages
- [kafkacat과 jq, 기타 필수 쉘 명령어 사용법](https://github.com/YunanJeong/kafka-test/blob/main/memo/memo_kafkacat_and_jq.md)
