# connect-settings

connect-distributed.properties에서 자주 건드리는 설정 모음

## 커넥트에서 하는 producer 설정

prefix(`producer.`)를 붙이면 커넥트에서도 producer속성을 설정할 수 있다. 소스 커넥터를 등록할 때 간과할 수 있다. 소스 커넥터에서 아무리 batch.size, flush 주기 등을 조정해도 connect에서 broker로 전송하는 데 지연이 발생하면 데이터 래깅, 리소스 사용량 증가 현상이 발생할 수 있다.

### producer.batch.size

- 설명: producer가 broker로 레코드 전송시 한번에 묶는 수. 요청 수를 줄이기 위해 있는 기능.
- 단위: 레코드 개수
- Default: 16384
- 작용
  - (데이터량에 비해) 값이 작으면 broker로 전송 처리량 감소
  - 많으면 메모리 낭비

### producer.buffer.memory

- 설명: producer가 broker로 레코드 전송하기 전, 버퍼링할 때 사용하는 바이트 수
- 단위: bytes
- Default: 33554432 (32MB)
- 작용
  - (broker가 수용가능한 데이터처리량에 비해) 값이 작으면 `max.block.ms` 동안 블로킹한뒤 익셉션 발생.
  - 값이 크면, 메모리 낭비
- batch.size만큼 레코드가 쌓일 경우, 이 설정과 무관하게 즉시 Produce 실행

### producer.max.block.ms

- `buffer.memory` 설명 참고

### producer.linger.ms

- 설명: producer가 produce 하기 전 지연시간
- Default: 0. Producer는 기본적으로 쌓이는 레코드를 지연없이 즉시 broker로 produce한다.
- 단, produce를 위해 request하는 시간동안 쌓이는 레코드들이 있는데, 이걸 다음 request에 한번에 보내는 것이다.
- 작용: linger.ms 값이 클수록 produce 한 번에 보내는 batch 사이즈가 커지고, 단위시간당 request 수는 감소한다.

## 커넥트 자체 설정

### offset.flush.interval.ms

- 설명: 오프셋 커밋 주기 설정
- 작용
  - 값이 작으면, 오프셋 커밋을 너무 자주해서, 커넥트의 메모리 사용량이 증가할 수 있다. 특히 task가 많을수록 더 심해질 수 있다.
  - 값이 크면, 오프셋 커밋을 별로 안해서, 재기동 or 복구 시 오래걸릴 수 있다.

### offset.flush.timeout.ms

- 설명: connect가 broker에 오프셋 커밋을 하고 응답을 기다리는 시간
- 작용
  - 값이 작으면, broker로부터 정상응답을 받기 전에 timeout이 나서, 커밋 failed가 발생할 수 있다.
  