# kafka_timestamp_management

## 많은 시스템에서 개발자들이 보편적으로 시간 유형을 지칭하는 법

- <https://developer.confluent.io/patterns/stream-processing/wallclock-time/>

### Event Time

- 이벤트 소스에서 이벤트 발생 순간 생성된 시간
- Raw Data에 있는 시간

### Ingestion Time

- Raw Data가 다른 플랫폼으로 옮겨졌을 때 해당 플랫폼에 적재된 시스템 시간

### Processing Time (Wall-clock Time)

- 데이터 파이프라인의 중간, 또는 최종 앱에서 처리된 시스템 시간

### 예시

- 아래 Record 예시에서 `일반적으로` 다음과 같이 볼 수 있음
- Event Time: value필드 안 Raw Data의 timestamp (RecordField 시간)
- Ingenstion Time: top level의 메타데이터 timestamp (Record 시간)

```json
{
  "topic": "user-activity",
  "partition": 3,
  "offset": 42,
  "timestamp": 1696512480000,  # => Ingestion Time (Metadata)
  "key": "user123",
  "value": "{\"action\": \"login\", \"timestamp\": \"2023-10-05T14:48:00Z\"}",  # => Event Time (Rawdata)
}
```

## 외부 시스템이 이벤트 소스인 경우

- 외부 이벤트 소스(DB)에서 Kafka로 데이터를 옮겨온 후, 이를 S3로 보내는 상황이라고 가정하자.
- S3에서 시간 기준으로 파티셔닝할 때, 어떤 시간을 기준으로 할 것인가 지정하는 S3 Sink Connector의 timestamp 옵션이 있음

### Record

- Ingestion Time
- kafka 토픽에 적재된 시간
- Record의 메타데이터 timestamp

### RecordField

- Event Time
- Record의 Value(Raw Data)에 있는 시간
- e.g. s3 sink connector에서 timestamp속성 값으로 RecordField를 쓰면, `timestamp.field` property를 추가로 써서 record 안의 특정 시간 필드를 지정가능

### WallClock

- Processing Time (Wall-clock Time)
- S3 Sink Connector가 최종적으로 데이터를 처리한 시각 기준 (broker 시간 아님)

## Kafka Producer 자체가 이벤트 소스인 경우 (메타데이터 timestamp 관리)

- 실제 데이터에서 어떤 시간이 EventTime, IngestionTime인지는 Event가 무엇이냐에 따라 달라질 수 있음
- `일반적으로 Kafka Record의 메타데이터 timestamp는 Ingestion Time`이라고 보면 되지만,
- `Producer 앱 자체가 이벤트 소스이고, 별도의 timestamp 필드를 value 값에 남기지 않는 경우, 자동생성된 메타데이터 timestamp를 이벤트 생성시각(EventTime)으로 사용할 수도 있다.`
- 이런 경우를 대비해서 Kafka는 메타데이터 timestamp 기록 방법을 두 가지 타입으로 나누고 있다.
- 어느 타입으로 쓸 지는 토픽 설정에 따라 달라지며, `server.properties`에서 신규 토픽 생성시 기본값도 설정가능 [(공식문서)](https://kafka.apache.org/documentation/#brokerconfigs_log.message.timestamp.type)

```properties
# server.properties
log.message.timestamp.type=LogAppendTime
```

### CreateTime (default)

- 메시지가 Producer에 의해 생성된 시각
- 특징
  - 동일 Kafka 내에서 Streams 등으로 처리 후 신규 토픽에 입력해도 기존 메타데이터 timestamp가 유지됨
  - 일반적인 경우 Ingestion Time으로 취급하여 사용해도 되나, LogAppendTime과 비교하면 Event Time에 가까움

### LogAppendTime

- 메시지가 Kafka 브로커에 추가된 시각(Record가 Topic에 적재된 시각)
- 특징
  - 진정한 의미로 IngestionTime에 가까움
  - 데이터 처리후 신규토픽에 적재시 항상 신규 메타데이터 timestamp가 부여됨

### 참고

- 특히 `메타데이터 timestamp는 retention.ms 등 보유기간 설정의 기준이 되는 값`이므로 이 때 CreateTime, LogAppendTime 설정에 유의한다.
