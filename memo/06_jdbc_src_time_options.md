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
