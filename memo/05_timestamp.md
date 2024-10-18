# kafka_timestamp_management

## 많은 시스템에서 개발자들이 시간 유형을 지칭하는 보편적 방법

- 이는 Event를 무엇으로 보는지 관점에 따라 바뀔 수 있음
- <https://developer.confluent.io/patterns/stream-processing/wallclock-time/>

### Event Time

- 이벤트 소스에서 이벤트 발생 순간 생성된 시간
- Raw Data에 있는 시간

### Ingestion Time

- Raw Data가 다른 플랫폼으로 옮겨졌을 때 해당 플랫폼에 적재된 시스템 시간

### Processing Time (Wall-clock Time)

- 데이터 파이프라인의 중간, 또는 최종 앱에서 처리된 시스템 시간

## S3 Sink Connector에서

- 다른 이벤트 소스(DB)에서 Kafka로 데이터를 옮겨온 후, 이를 S3로 보내는 상황이라고 가정하자.
- S3 저장시 시간 기준으로 파티셔닝 할 때, 어떤 시간을 기준으로 할 것인가 지정하는 timestamp 옵션이 있음

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
- S3 Sink Connector가 최종적으로 데이터를 처리한 시각 기준 (broker 시간아님)

## 메타데이터 timstamp

```json
# Kafka Message 구조
```

```properties
# server.properties
# 신규생성 토픽에서 Record의 메타데이터 timestamp 타입  # default: CreateTime
log.message.timestamp.type=LogAppendTime
```

### CreateTime

- 메시지가 Producer에 의해 생성된 시각
- Kafka Streams 등으로 처리 후 신규 토픽에 입력해도 기존 timestamp가 유지됨
- default


### LogAppendTime

- 메시지가 Kafka 브로커에 추가된 시각(토픽에 적재된 시각)
- 데이터 처리후 신규토픽에 적재시 신규 timestamp가 부여됨
