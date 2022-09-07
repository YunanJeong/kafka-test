# JDBC Source Connector 시간 관련 옵션 정리
- poll.interval.ms (Connector)
	=> 각 테이블에 새 데이터를 폴링(커넥트쪽에서 DB로 요청, 상태점검, 동기화 등)하는 빈도
- table.poll.interval.ms (Connector)
	=> 새 테이블 또는 삭제된 테이블에 대해 폴링하는 주기
	=> ??? 이해가 잘안됨. 테이블삭제or 생성되면 config 내용이 자동으로 바뀐다는 말인가?
	=> whitelist, blacklist 설정이 아니라 db 전체 테이블 대상이면 말이되네.
- timestamp.delay.interval.ms (Connector) (default: 0ms)
	=> 특정 타임스탬프가 있는 행이 나타난 후 결과에 포함되기 전에 대기하는 시간
- connection.backoff.ms (Database)
	=> DB 연결시 백오프 시간 (네트워크 연결 실패시 backoff 시간만큼 기다렸다가 재시도)