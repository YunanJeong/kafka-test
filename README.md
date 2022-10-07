# kafka-test
kafka-test

## 디렉토리
```
├── README.md
├── basic-instance/
├── kafka-broker-basic/
├── kafka-broker-connect-basic/
├── kafka-broker-connect-systemd/
├── kafka-control/
├── kafka-jdbc-connector-test/
├── kafka_timestamp_management.md
├── memo_jdbc_src_con_options.md
├── memo_s3_sink_con_options.md
├── python-kafka-test/
└── test-db-broker-s3/
```

## 봐야할 내용
1. kafka 기본
2. CDC, CT 방식중 CT 방식 먼저
3. JDBC 소스커넥터로 db->kafka로 데이터 옮기는 구조 만들기
=> 클러스터 만들지말고 우선 노드 1개로 빠르게 세팅 해보기
4. 이후 클러스터 구성해보기

## Record - Kafka Message Structure
- kafka에서 가장 작은 메시지 단위는 Record라고 부른다.
	- Record = Message = Event = Data = log 1줄 이라고 보면 된다.
- 한 Record 안에는 Headers, key, value가 들어있다.
	- 이 중 Headers에는 topic, partition, timestamp 정보가 있으며, MetaData라고 보면된다.
	- key, value는 일반적으로 Body 또는 Business Relevant Data 라고 표현되는 부분이다. (원본 데이터 내용)

- https://www.google.com/search?q=kafka+record+timestapme&tbm=isch&ved=2ahUKEwib6f2Lm4L6AhXPZ94KHWiqBJ0Q2-cCegQIABAA&oq=kafka+record+timestapme&gs_lcp=CgNpbWcQAzoECCMQJzoECAAQEzoGCAAQHhATOgUIABCABDoECAAQHjoECAAQGFDQB1iRKWD3LWgAcAB4AIABcYgB_BqSAQUxNC4yMJgBAKABAaoBC2d3cy13aXotaW1nwAEB&sclient=img&ei=ZU8YY9uiIs_P-Qbo1JLoCQ&bih=969&biw=1920&rlz=1C1GCEA_enKR959KR967#imgrc=0ffhDAgddKBNRM


## 설치 후 빠른 실행시 확인해야할 것
- server.properties
	- advertised.listeners에 해당 broker에 해당하는 hostname(또는 ip) 기술
	- log.dirs는 record가 저장되는 장소다.(서버, 시스템 로그를 의미하지 않는다.)
		- 디폴트가 /tmp 로 되어있는데, 이는 os에서 삭제해버릴 수도 있는 경로다. /data를 생성해서 써주자.
- connect-distributed.properties
	- connector plugin 경로 지정
- file descriptor 설정
	- systemd 서비스 실행시, 서비스파일에서 설정해야 함
- s3 sink connector 사용시 AWS KEY
	- 실행환경에서 ~/.aws/credentials 파일만 있으면 됨.
	- systemd 서비스 실행시, 서비스파일에서 설정해야 함
- log4j 설정
	- 카프카의 config 경로에 broker용과 connect용 설정이 별도로 있음
	- systemd 서비스 실행시,
		- 설정 파일에서 stdout을 지우면, syslog에도 로그가 남지 않음
		- 카프카 logs 경로에 남는 로그파일은 syslog(stdout)과 별도로 남음

## kafkacat 활용
- 설치: `sudo apt install kafkacat`
- -L: List, 메타 정보 조회
- -b: broker 지정
- -t: topic 지정
- -p: partition 지정
- -q: quiet
- -P: Producer Mode
- -C: Consumer Mode

- 예시)
	- broker: localhost:9092
	- topic's name: topicname
- `$ kafkacat -b localhost:9092 -L`
	- 해당 브로커의 메타정보를 보여준다.
	- 브로커, 토픽, 파티션 목록을 보여 준다.
- `$ kafkacat -b localhost:9092 -t topicname -L`
	- 브로커와 토픽을 지정하고, L옵션을 설정
	- 해당 토픽에 한정해서 메타정보를 보여준다.
- `$ kafkacat -b localhost:9092 -t topicname`
	- 브로커와 토픽을 지정
	- 기본적으로 Consumer mode로 취급되어 해당 토픽의 Record를 보여준다.
	- `$ kafkacat -b localhost:9092 -t topicname -C` 와 동일
	- 지정 토픽이 존재하지 않는 경우, Consume을 수행했을 때
		- kafka 내장 쉘명령어는 해당 빈 토픽을 자동생성하지만,
		- kafkacat은 자동생성하지 않고 에러를 출력한다.
- `$ kafkacat -b localhost:9092 -t topicname -P`
	- 브로커와 토픽을 지정하고, Producer mode로 설정했다.
	- 쉘에서 입력한 내용이 토픽의 Record로 저장된다.
	- 다른 쉘에서 Consumer mode를 열어놓고 실시간으로 확인해볼 수 있다.
	- 지정 토픽이 존재하지 않는 경우, 자동 생성한다.
- `$ kafkacat -b localhost:9092 -t topicname -q`
- `$ kafkacat -b localhost:9092 -t topicname -e`