# kafka_timestamp_management
    - `WallClock`: Processing Time. 데이터 파이프라인의 최종앱에서 처리된 시스템 시간.(이 경우 sink connector가 처리한 시간)
    - `Record`: Ingestion Time에 가까움. Record의 Headers(메타데이터)에 있는 timestamp (즉, kafka 토픽에 적재된 시간)
    - `RecordField`: Event Time. 원본로그의 시간. "timestamp.field항목을 추가로 써서 record의 특정 시간 필드를 지정할 수 있음
    - 각 시간옵션: https://developer.confluent.io/patterns/stream-processing/wallclock-time/
