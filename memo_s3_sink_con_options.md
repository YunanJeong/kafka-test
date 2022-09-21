# S3 Sink Connector 시간 관련 옵션 정리
- `rotate.interval.ms`
	- s3에 파일 커밋(flush하고, 새 파일을 생성)하는 주기
	- flush.size와 함께 둘 중 먼저 만족하는 조건대로 파일 커밋된다.
	- 시간 기준
		- timestamp extractor로 지정된 시간 (WallClock, Record, RecordField)
		- 시간 구간의 기준점(시작점)은 first record(맨 처음 입력된 record)의 시간이다.
		- e.g.) `RecordField 기준`으로 60000ms(1분) 설정한 경우,
			- Event Time이 "0시 1분"인 record가 first record로 입력되었다면,
			- "0시 1분 ~ 0시 1분 59.999초" 로 기록된 모든 record들은 전부 한 파일에 들어간다.
			- 위 time interval에 해당하는 record가 계속 무한정 입력되면,
			 	- flush.size를 만족할 때까지 파일 커밋이 되지 않는다.
				- 테스트시 똑같은 데이터로 실험할 경우 주의
				- 계속 한 파일에 대해 open상태로 write 대기해야 하므로 메모리 이슈 등 가능성
			- 위 time interval을 벗어나는 record가 입력되면,
				- 파일 커밋된다.
				- 데이터가 순차적으로 입력되면 문제없다.
				- 과거데이터, 지연데이터가 들어오면 flush size를 무시하고 현재 작업을 파일 커밋한 후, 새로운 파일에 과거데이터를 기록한다.
				- 이는 결과값을 얻는데는 문제없으나, 많은 file open/close로 인한 리소스 문제와 S3 비용 문제를 야기할 수 있다.
			- 서로 다른 시간대의 데이터를 동시에 지속적으로 입력받으면,
				- flush.size를 무시하고 파일이 무한정으로 나뉘어지는 상황이 발생된다.
			- 커넥터에 다음 처리할 record가 입력되지 않으면,
				- 커넥터는 file open 상태로 무한정 대기한다.
				- flush.size와 rotate.interval.ms 값이 모두 매우 크면 문제가 있다.
			- 장점:
				- 한 파일 내 로그들은 특정 시간구간에만 해당한다는 것을 정확히 보장할 수 있다.

- `rotate.schedule.interval.ms`
	- s3에 파일 커밋(파일을 새로 생성)하는 주기
	- flush.size와 함께 둘 중 먼저 만족하는 조건대로 파일 커밋된다.
	- 시간 기준
		- 시스템 시간
		- timezone의 0시 0분을 기준으로 삼는다.
		- e.g. 1) 3600000ms(1시간)으로 설정하고, flush.size는 매우 큰 값인 경우,
			- 0시, 1시, 2시, ... 일 때 새 파일이 생성된다.
		- e.g. 2) 3000000ms (50분)으로 설정하고, flush.size는 매우 큰 값인 경우,
			- 0:50, 1:40, 2:30, ... 일 때 새 파일이 생성된다.
	- timestamp extractor는 s3 path(partition)을 나누는데에만 관여한다.
		- timestampe extractor가 RecordField일 떄, 
			- EventTime에 맞는 partition으로 자동 분배되고, 지정 rotate시간이 되면 s3에 별도 파일로 각각 커밋된다.

	- 커넥터에 다음 처리할 Record가 없을 때
		- connect worker의 `offset.flush.interval.ms` 옵션에 따라, 커넥터는 계속 호출된다.
		- 이 때 커넥터는 현재 시각 기준으로 현재 open된 파일을 닫고, s3 업로드 할지말지 여부를 결정한다.
		- 참고: `offset.flush.interval.ms`
			- connect의 설정이다.
			- 태스크에서 오프셋 커밋을 시도하는 간격을 의미하며, default는 60000

- rotate.interval.ms에서 WallClock모드와 rotate.schedule.interval.ms 비교
	- 둘 다 시스템 시간 기준인데 무슨 차이가 있을까?
	- 차이점: s3 경로(파티션)을 나누는 기준이 다르다.
		- rotate.interval.ms 사용시,
			- timestamp extractor에서 지정한 모드에 따라 s3경로 구분과 rotate를 둘 다 처리한다.
			- Wallclock 모드 사용시, s3경로 구분도 시스템 시간 기준으로 구분돼서 EventTime에 따라 record를 분류할 수 없다.
			- RecordField 모드 사용시, s3 경로구분과 rotate 모두 EventTime기준으로 처리한다.
		- rotate.schedule.interval.ms
			- rotate 시간만 시스템 시간 기준이다.
			- 시간에 따른 s3 경로 구분은 timestamp extractor의 설정에 따른다.

- flush size가 매우 크고, rotate 시간 설정이 없을 때의 문제점
	- 데이터 손실가능성
		- flush되지 않은 데이터는 s3 sink의 메모리에 남아있다.
		- s3 sink가 비정상종료, 또는 교체 등 이유로 종료되면 증발한다.
		- 시간이 오래 지났을 경우 broker topic에도 삭제되었을 수 있다.
		- https://stackoverflow.com/questions/50761999/how-can-we-force-confluent-kafka-connect-s3-sink-to-flush

- 결론: 그래서 뭐 써야 하나? (220921 개인 메모)
	- 내 작업에서는 일단 rotate.schedule.interval.ms 사용하고, path 구분을 위한 timestamp extractor는 RecordFiled(EventTime)을 사용하는 것이 무난해보인다.
	- 당연히 상황에 따라 옵션은 달라질 수 있다. 

- `retry.backoff.ms` (default: 5000ms)
	- connector와 connect사이에서 메시지 전송실패 등 예외상황 발생시 retry하는 backoff시간
- `s3.retry.backoff.ms`
	- s3 request 실패시 처음 재시도할 때까지 기다릴 시간(backoff time)
- `partition.duration.ms`
	- TimeBasedPartitioner 사용시, s3 상에 path.format 경로(파티션)을 생성하는 주기
	- 파티션을 시간단위로 나눈다면 이 옵션은 3,600,000 ms 로 설정되어야 한다.

# S3 Sink Connector에서 Exacltly-Once Delivery
- Exactly-once delivery on top of eventual consistency
	- 문서: https://docs.confluent.io/kafka-connectors/s3-sink/current/overview.html#streaming-etl-demo
	- 중복, 손실없이 정확히 한번 전송을 보장하는 방법을 기술하고 있다.
	
- 다음과 같은 deterministic한 방법을 써야한다.
	- TimeBasedPartitioner 옵션 사용
	- TimestampExtractor 옵션은 Record or RecordField로 설정
	- rotate.interval.ms 옵션 사용

- 그럼에도 불구하고 보장되지 않는 케이스
	- late data possible?
		- 늦게들어오는 데이터의 존재 가능성이 있으면 Exactly-Once Delivery가 보장되지 않는다.
			- 정확하지 않음. 공식문서가 너무 불친절&간결하다.
- 데이터 전송 중 S3 Sink Connector를 교체하는 경우
	- 어지간하면 중복, 손실이 없다. 최소한 중복은 있어도 손실은 없다. (At-least-Once Delivery 수준)
		- 다만 At-least-Once도 Exactly-Once도 이 경우 '보장'하는 수준은 아닌 것 같다.
