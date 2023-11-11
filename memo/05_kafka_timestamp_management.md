# kafka_timestamp_management

## WallClock

- Processing Time
- 데이터 파이프라인의 최종앱에서 처리된 시스템 시간
- e.g. s3 sink connector의 timestamp속성 값으로 WallClock을 쓰면 sink connector가 처리한 시간을 의미함.(broker 아님)

## Record

- Ingestion Time
- kafka 토픽에 적재된 시간
- Record의 Headers(메타데이터)에 있는 timestamp

## RecordField

- Event Time
- Raw Data에 있는 시간
- e.g. s3 sink connector에서 timestamp속성 값으로 RecordField를 쓰면, `timestamp.field` property를 추가로 써서 record 안의 특정 시간 필드를 지정가능

## 각 시간옵션 관련 설명

<https://developer.confluent.io/patterns/stream-processing/wallclock-time/>
