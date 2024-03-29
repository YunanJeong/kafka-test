# topic settings

자주 설정하는 토픽 옵션 정리

## Default

최초 설정값은 토픽생성시 준 옵션, Producer설정, server.properties 등에 의해 결정된다.

또한, Default는 Kafka 버전마다 다를 수 있다.

## segment 관련

- 카프카 데이터는 segment라고 불리는 파일 단위로 저장된다.
- 저장경로: `server.properties`의 `log.dirs`로 결정됨
- segment는 topic 파티션 별로 생성된다.

### segment.ms

- 지정된 시간을 초과하면 새로운 segment로 롤링
- segment 파일이 open된 시점 기준으로 지정시간 초과시 closed됨

```sh
# server.properties에서 신규 생성 토픽의 default segment.ms 변경
log.roll.ms=172800000
```

### segment.bytes

- 지정 용량을 초과하면 새로운 segment로 롤링

### segment.index.bytes

- index: 메시지의 오프셋과 파일 내 위치를 매핑
- 검색 속도에 영향 줌
- 보통 default로 두면됨

### segment.jitter.ms

- segment 롤링 트리거에 무작위 지연시간을 부여하여 모든 브로커에서 동시에 롤링이 발생하는 것을 방지
- 부하 분산용
- 0이면 무작위성 없음

## retention 관련

Kafka가 쓰는 중인 파일open된 segment는 적용대상이 아님

오동작 방지를 위해 가급적 retention은 segment보다 큰 값으로 설정 필요

### retention.ms

- closed segment 내부 모든 record가 지정시간을 초과하면 해당 segment를 삭제 취급
- segment 내부에 지정시간을 초과하지 않은 record가 하나라도 있으면, 삭제되지 않음

### retention.bytes

- topic의 closed segment들이 지정용량을 초과하면 삭제 취급
- 개별 segment가 아닌, **대상 topic의 모든 closed segment들 용량 합산**으로 계산
- `-1`: 용량제한 없음

### delete.retention.ms

- `retention.ms`, `retention.bytes`에 의한 처리 이후, 지정시간을 초과하면 실제 segment 파일을 삭제
