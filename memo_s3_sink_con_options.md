# S3 Sink Connector 시간 관련 옵션 정리
- `rotate.interval.ms`
	- 한 파일에 기록될 시간구간의 최댓값
	- ex) 1시간이면 최대 1시간크기의 파일이 만들어 진다.
		- 1시간보다 적을 수도 있다.
		- 말이 헷갈리는데 flush.size랑 비슷한 개념. flush.size는 한 파일 내 최대 로그 개수를 다루지만, 이건 한 파일 내 최대 시간 구간을 다룬다.
	- 이 옵션으로 지정한 시간만큼 계속 한 파일에 write를 해야 하므로, 해당 시간 동안은 file open 상태이다.
	- 지정 시간이 지나면, 커넥터는
		- 기존 write하던 파일을 flush하고, s3로 업로드 한다.(각 record에 대한 offset도 이 때 커밋한다.)
		- 다른 옵션들을 무시하고 새 파일에다가 write를 한다. ("최대"시간구간을 지정하는 것이니까)
	- 시간 구간의 기준점(시작점)은 first record의 시간이다.
		- first record의 시간은 timestamp.extractor 옵션에 따라 차이가 있을 수 있다.(record의 특정시간필드 값 등)
	- 커넥터에 다음 처리할 레코드가 없을 때
		- 커넥터가 파일을 쓸데없이 open 상태로 두어 시간이 오래 걸릴 수 있음

- `rotate.schedule.interval.ms`
	- 기본적으로 `rotate.interval.ms`와 동일
	- 차이점: first record가 "파일"에 쓰여진 "(커넥터 서버)시스템 시간"을 시간구간의 기준시작점으로 삼는다.
	- 현재 시간에 따른 처리를 해야할 때 유용하다.
	- timezone 옵션 세팅을 확인해야 한다.
	- 커넥터에 다음 처리할 레코드가 없을 때
		- connect worker의 offset.flush.interval.ms 옵션에 따라,
		- 커넥터는 계속 호출된다. 이 때 커넥터는 현재 시간 기준으로 현재 open된 파일을 닫고, s3 업로드 할지말지 여부를 결정한다.

- flush size가 매우 크고, rotate 시간 설정이 없을 때의 문제점
	- 데이터 손실가능성
		- flush되지 않은 데이터는 s3 sink의 메모리에 남아있다.
		- s3 sink가 비정상종료, 또는 교체 등 이유로 종료되면 증발한다.
		- 시간이 오래 지났을 경우 broker topic에도 삭제되었을 수 있다.
		- https://stackoverflow.com/questions/50761999/how-can-we-force-confluent-kafka-connect-s3-sink-to-flush

- `retry.backoff.ms` (default: 5000ms)
	- connector와 connect사이에서 메시지 전송실패 등 예외상황 발생시 retry하는 backoff시간
- `s3.retry.backoff.ms`
	- s3 request 실패시 처음 재시도할 때까지 기다릴 시간(backoff time)
- `partition.duration.ms`
	- TimeBasedPartitioner 사용시, s3 상에 path.format 경로(파티션)을 생성하는 주기
	- 파티션을 시간단위로 나눈다면 이 옵션은 3,600,000 ms 로 설정되어야 한다.

# S3 Sink Connector에서 Exacltly-Once Delivery
- Exactly-once delivery on top of eventual consistency
	=> https://docs.confluent.io/kafka-connectors/s3-sink/current/overview.html#streaming-etl-demo
- 다음과 같은 deterministic한 방법을 써야한다.
	- TimeBasedPartitioner, TimestampExtractor(Record, RecordField)
	- rotate.interval.ms 설정

- late data possible?
	- 늦게들어오는 데이터가 있을지 가능성에 대해 얘기하는 것 같은데, 공식문서 설명이 너무 불친절&간결하다.
