# jdbc source connector 시간 관련 옵션 정리

- poll.interval.ms (Connector)
  - 각 테이블에 새 데이터가 있는지 폴링(커넥트쪽에서 DB로 요청, 상태점검, 동기화 등)하는 빈도
- table.poll.interval.ms (Connector)
  - 새 테이블 또는 삭제된 테이블을 인식하기 위하여 폴링하는 주기
  - whitelist, blacklist 설정으로 이미 table을 지정한 경우에는 큰 의미가 없어 보인다.
  - DB 전체 테이블 대상으로 데이터 추출시 rotation 등이 발생할 때 더 중요한 옵션인 듯 싶다.
- timestamp.delay.interval.ms (Connector) (default: 0ms)
  - 특정 타임스탬프가 있는 행이 나타난 후 결과에 포함되기 전에 대기하는 시간
  - 해당 타임스탬프보다 이전시간의 타임스탬프를 가진 트랜잭션이 순차적으로 완료될 수 있도록 기다리는 시간이라고 볼 수 있다.
- connection.backoff.ms (Database)
  - DB 연결시 백오프 시간 (네트워크 연결 실패시 backoff 시간만큼 기다렸다가 retry)

## <시간 정밀도가 낮을 때 데이터 누락 방지 하는 법>

### timestamp mode에서 누락이 발생하는 전형적인 사례

- 특히, 시간정밀도가 낮을수록 더 심함
- 동 시간 timestamp로 여러 row가 생성될 때, 쿼리타이밍이 해당 시간과 겹치는 경우
- timestamp 값이 DB 테이블에 적재되는 순간 생성되는 게 아니라 외부에서 insert하는 값일 때 insert 트랜잭션처리시 딜레이가 발생하거나 적재순서가 꼬이는 경우

### 해결방법

- `timestamp.delay.interval.ms` > `poll.interval.ms`(쿼리주기) > `소스DB트랜잭션(insert) 지연` 과 같이 설정하면 99.999999999% 누락 위험을 피할 수 있다고 보면된다.
- 핵심은 `timestamp.delay.interval.ms`이 소스 DB 트랜잭션 지연 보다 충분히 길도록 설정하는 것으로, `매우 높은 수준의 실시간성이 요구되는게 아니라면` 넉넉하게 설정해주자.
- 쿼리구조 상 `timestamp.delay.interval.ms`를 `poll.interval.ms`(쿼리주기)보다 길게 설정시, 더 강건한 누락방지 처리가 가능하다.

### jdbc source connector timestamp mode 의 내부 쿼리 구조

```
SELECT * FROM table_name 
WHERE timestamp_column > ? AND timestamp_column < ?
ORDER BY timestamp_column ASC
```

```
SELECT * FROM table_name 
WHERE timestamp_column > ?(이전 쿼리에서 가져온 데이터중 가장 큰 timestamp 값)
  AND timestamp_column < ?(현재시간 - timestamp.delay.interval.ms)
ORDER BY timestamp_column ASC
```