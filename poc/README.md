# PoC for Kafka deploy & initial Setup

Kafka configuration by installation type

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
├── README.md
├── py-connect-examples             # Test connectors
└── py-connect-util                 # Simple library to manage connectors

```

## Record: Kafka Message Structure

Kafka의 가장 작은 메시지 단위를 Record라고 부른다.

Record = Message = Event = Data = log 1 row 이라고 보면 된다.

### Record 구조 [(Official)](https://kafka.apache.org/documentation/#record)

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

### Record 구조를 직관적으로 나타낸 것 (주로 이거보면 됨)

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

### 필드 별 용도 (메타 데이터)

- **Kafka 시스템이 Record를 분류**하기 위한 정보를 자동 기록
- topic
  - Record가 저장된 topic 명
- partition
  - Record가 저장된 partition number
- offset
  - Record에 부여된 Offset number
- **timestamp**
  - Record마다 메타 데이터로 기록된 시간
  - **retention 설정 기간의 기준값**
  - 다음 두 타입 중 선택가능
  - **CreateTime(default)**
    - 메시지가 프로듀서에 의해 생성된 시각
    - KStreams 등으로 Record를 재처리 후 신규토픽에 적재해도 CreateTime은 유지됨
  - **LogAppendTime**
    - 메시지가 Topic에 적재된 시각

### 필드 별 용도 (Business Data)

- **key**
  - Kafka 사용자가 Record를 분류하기 위한 정보를 기록
  - 동일한 key를 가진 Record는 동일한 Partition에 저장됨
  - 메시지의 순서보장이 필요한 경우, 동일 key를 부여하여 단일 partition에 저장하는 방식이 활용됨
  - key 미사용시, 한 토픽 내에서 라운드로빈으로 균등하게 파티션마다 Record가 분배됨
- **value**
  - 핵심 Business Data, Payload, Raw Data에 해당
  - schema정보 활용시 value에 포함됨
  - schema registry 사용시 value 내부에 schema_id 필드를 기입하는 방식
- headers
  - 사용자가 추가적으로 데이터 분류시 사용할 헤더를 key-value 형태로 기입 가능
  - **key필드와 달리, Kafka 시스템은 headers를 데이터 분류에 사용하지 않음.** 단순히 추가 정보 작성할 수 있는 자리만 제공하는 것임.

