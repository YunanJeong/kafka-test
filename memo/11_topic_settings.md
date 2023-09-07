# topic settings

카프카의 토픽 옵션 정리

## Default

최초 설정값은 토픽생성시 준 옵션, Producer설정, server.properties 등에 의해 결정된다.

또한, Default는 Kafka 버전마다 다를 수 있다.

## segment 관련

- 카프카 데이터는 segment라고 불리는 파일 단위로 저장된다.
- 저장경로: `server.properties`의 `log.dirs`로 결정
- segment는 topic 파티션 별로 생성된다.

### segment.ms

- 지정된 시간을 초과하면 새로운 segment로 롤링

### segment.bytes

- 지정 용량을 초과하면 새로운 segment로 롤링

## retention 관련

Kafka가 쓰는 중인 파일open된 segment는 적용대상이 아님

### retention.ms

- closed segment 내부 모든 record가 지정시간을 초과하면 해당 segment를 삭제 취급
- segment 내부에 지정시간을 초과하지 않은 record가 하나라도 있으면, segment는 삭제되지 않음

### retention.bytes

- topic의 closed segment들이 지정용량을 초과하면 삭제 취급
- 개별 segment가 아닌, **대상 topic의 모든 closed segment들 용량 합산**으로 계산

#### delete.retention.ms

- `retention.ms`, `retention.bytes`에 의한 처리 이후, 지정시간을 초과하면 실제 segment 파일을 삭제
