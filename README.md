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

### Record 공식 구조(https://kafka.apache.org/documentation/#record)

```sh
length: varint
attributes: int8
    bit 0~7: unused
timestampDelta: varlong
offsetDelta: varint
keyLength: varint
key: byte[]
valueLen: varint
value: byte[]
Headers => [Header]
```

### Record 구조를 직관적으로 나타낸 것

```sh
Kafka Record
├── Topic      
├── Partition
├── Offset
├── Timestamp
├── Key (Optional)
├── Value
└── Headers
    ├── Header 1
    │   ├── Key
    │   └── Value
    ├── Header 2
    │   ├── Key
    │   └── Value
    └── ...
```

### Record 예시

- Kafka는 데이터를 bytes 배열로 저장
- 다음은 Record를 Json으로 Deserialization하여 출력한 예시

```json
{
  "topic": "user-activity",
  "partition": 3,
  "offset": 42,
  "timestamp": 1696512480000,
  "key": "user123",
  "value": "{\"action\": \"login\", \"timestamp\": \"2023-10-05T14:48:00Z\"}",
  "headers": [
    { "key": "source", "value": "web" },
    { "key": "version", "value": "1.0" },
    { "key": "correlationId", "value": "abc123xyz" }
  ]
}
```

### 필드 별 용도 (Record 메타 데이터)

- **Kafka 시스템이 Record를 분류**하기 위한 정보를 자동 기록
- topic
  - Record가 저장된 topic 명
- partition
  - Record가 저장된 partition number
- offset
  - Record에 부여된 Offset number
- timestamp
  - 메타 데이터로 기록된 시간
  - CreateTime:
  - LogAppendTime: 

### 필드 별 용도 (Business Data)

- **key**
  - **Kafka 사용자가 Record를 분류**하기 위한 정보를 기록
- **value**
  - 핵심 Business Data, Payload, Raw Data에 해당
  - schema정보 포함시 value에 포함됨
  - schema registry 사용시 value에 schema_id 필드를 기입하는 방식
- headers
  - 사용자가 추가적으로 데이터 분류시 사용하고 싶은 헤더를 key-value 형태로 기입 가능
  - Kafka 시스템은 이 정보를 데이터 처리에 사용하지 않는다. 단순히 추가 헤더 작성할 수 있는 자리만 제공하는 것일 뿐임

## 메모

0. [Kafka 라이센스 정리](https://github.com/YunanJeong/kafka-test/blob/main/memo/0_kafka_license.md)

1. [Kafka 설치, 실행, 설정](https://github.com/YunanJeong/kafka-test/blob/main/memo/1_kafka_install.md)

2. [Kafka 메시지 관리 및 분석 방법 (kafkacat, jq, 쉘 명령어)](https://github.com/YunanJeong/kafka-test/blob/main/memo/2_kafkacat_and_jq.md)

3. [Kafka Python Package 종류](https://github.com/YunanJeong/kafka-test/blob/main/memo/3_python_kafka_package.md)
    - Python으로 Producer, Consumer 만들 때 사용가능한 라이브러리

4. [topic의 offset, __consumer_offsets, connect-offsets](https://github.com/YunanJeong/kafka-test/blob/main/memo/4_offsets.md)
    - 특히 Source Connector를 위한 connect_offsets 설명 위주

5. [Kafka Timestamp 종류](https://github.com/YunanJeong/kafka-test/blob/main/memo/5_kafka_timestamp_management.md)

6. [JDBC src connector 시간 관련 옵션](https://github.com/YunanJeong/kafka-test/blob/main/memo/6_jdbc_src_time_options.md)

7. [S3 sink connector 시간 관련 옵션](https://github.com/YunanJeong/kafka-test/blob/main/memo/7_s3_sink_time_options.md)

8. [Kafka 복제도구: MirrorMaker1, MirrorMaker2, Replicator](https://github.com/YunanJeong/kafka-test/blob/main/memo/8_mirrormaker_replication.md)

9. [Connect에서 Converter 종류](https://github.com/YunanJeong/kafka-test/blob/main/memo/9_connect_converter.md)

10. [토픽튜닝할 것들(segment,retention 등)](https://github.com/YunanJeong/kafka-test/blob/main/memo/10_topic_settings.md)

11. [토픽튜닝: partition](https://github.com/YunanJeong/kafka-test/blob/main/memo/11_topic_settings_partition.md)

12. [토픽튜닝: replication](https://github.com/YunanJeong/kafka-test/blob/main/memo/12_topic_settings_replication.md)

13. [Connect 설정](https://github.com/YunanJeong/kafka-test/blob/main/memo/13_connect_settings.md)

14. [커넥터 등록, 업데이트, 삭제](https://github.com/YunanJeong/kafka-test/blob/main/memo/14_connector_control.md)

15. [커넥터 SMT 예시](https://github.com/YunanJeong/kafka-test/blob/main/memo/15_connector_smt.md)

16. [힙메모리 부족시 트러블슈팅](https://github.com/YunanJeong/kafka-test/blob/main/memo/16_heap_memory_troubleshoot.md)
