# kafka-test

kafka-test

## Tree

```sh
├── 0_kafka-broker-basic            # Set up kafka 1 node (zookeeper, broker) by Apache Kafka
├── 1_kafka-broker-connect-basic    # Add kafka connect to "module 0"
├── 2_kafka-broker-connect-systemd  # Run "module 1"'s kafka as systemd service
├── 3_kafka-jdbc-connector-test     # Add connectors(jdbc-src, s3-sink) to "module 2"
├── 4_kafka-ksql-service            # Add ksqlDB to "module 3"
├── 5_confluent-community-archive   # Set up kafka 1 node by Confluent Platform Community(zip or tar)
├── 6_confluent-community-package   # Set up kafka 1 node by Confluent Platform Community(deb)
├── 7_cclpkg-debezium-test          # Add debezium connector to "module 6" 
├── 8_legacy_kafka                  # Module For Old Kafka 1 node 
├── LICENSE
├── README.md
├── memo/                           # Tips for Kafka Operation
├── py-connect-examples             # Test connectors
└── py-connect-util                 # Simple library to manage connectors

```

## Record: Kafka Message Structure

Kafka의 가장 작은 메시지 단위를 Record라고 부른다.

Record = Message = Event = Data = log 1 row 이라고 보면 된다.

[참고 그림](https://www.google.com/search?q=kafka+record+timestapme&tbm=isch&ved=2ahUKEwib6f2Lm4L6AhXPZ94KHWiqBJ0Q2-cCegQIABAA&oq=kafka+record+timestapme&gs_lcp=CgNpbWcQAzoECCMQJzoECAAQEzoGCAAQHhATOgUIABCABDoECAAQHjoECAAQGFDQB1iRKWD3LWgAcAB4AIABcYgB_BqSAQUxNC4yMJgBAKABAaoBC2d3cy13aXotaW1nwAEB&sclient=img&ei=ZU8YY9uiIs_P-Qbo1JLoCQ&bih=969&biw=1920&rlz=1C1GCEA_enKR959KR967#imgrc=0ffhDAgddKBNRM)

### Header

- 메타데이터(topic, partition, timestamp(Ingestion Time) 등)
- **Kafka 시스템이 Record를 분류**하기 위한 정보를 자동 기록

### Body(Business Data)

- **key**
  - **Kafka 사용자가 Record를 분류**하기 위한 정보를 기록
- **value**
  - 핵심 Payload, 원본데이터에 가까움

## 메모

0. [Kafka 라이센스 정리](https://github.com/YunanJeong/kafka-test/blob/main/memo/0_kafka_license.md)

1. [Kafka 설치, 실행, 설정](https://github.com/YunanJeong/kafka-test/blob/main/memo/1_kafka_install.md)

2. [Kafka 메시지 관리 및 분석 방법 (kafkacat, jq, 쉘 명령어)](https://github.com/YunanJeong/kafka-test/blob/main/memo/2_kafkacat_and_jq.md)

3. [Kafka Python Package 종류](https://github.com/YunanJeong/kafka-test/blob/main/memo/3_python_kafka_package.md)
    - Python으로 Producer, Consumer 만들 때 사용가능한 라이브러리

4. [Connector를 위한 offset 다루기](https://github.com/YunanJeong/kafka-test/blob/main/memo/4_connect_offsets.md)
    - 특히 Source Connector를 위한 connect_offsets 설명 위주

5. [Kafka Timestamp 종류](https://github.com/YunanJeong/kafka-test/blob/main/memo/5_kafka_timestamp_management.md)

6. [JDBC src connector 시간 관련 옵션](https://github.com/YunanJeong/kafka-test/blob/main/memo/6_jdbc_src_time_options.md)

7. [S3 sink connector 시간 관련 옵션](https://github.com/YunanJeong/kafka-test/blob/main/memo/7_s3_sink_time_options.md)

8. [Kafka 복제도구: MirrorMaker1, MirrorMaker2, Replicator](https://github.com/YunanJeong/kafka-test/blob/main/memo/8_mirrormaker_replication.md)

9. [Connect에서 Converter 종류](https://github.com/YunanJeong/kafka-test/blob/main/memo/9_connect_converter.md)

10. [topic partition 개수 정하기](https://github.com/YunanJeong/kafka-test/blob/main/memo/10_kafka_partition_tuning.md)

11. [topic 개별 세팅](https://github.com/YunanJeong/kafka-test/blob/main/memo/11_topic_settings.md)
