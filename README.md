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
- 설치: `$ sudo apt install kafkacat`
- -L: List, 메타 정보 조회
- -b: broker 지정
- -t: topic 지정
- -p: partition 지정
- -q: quiet
- -e: exit
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
- `$ kafkacat -b localhost:9092 -t topicname -C -q`
	- Consumer Mode에서 q 옵션 사용시, Record 내용만 조회할 수 있다.
	- '새 메시지가 도착했다'라는 출력이 표시되지 않는다.
- `$ kafkacat -b localhost:9092 -t topicname -C -e`
	- e 옵션 사용시 마지막 내용까지 출력한 후 대기모드상태에 있지 않고 자동 exit한다.

## 쉘에서 메시지 관리&분석 하기
- 아래 명령어들은 모두 라인 단위로 이루어진다. (다른 라인끼리만 비교한다. 같은 라인 내에서 중복, 정렬 처리를 하지 않는다.)

- 중복제거 후 출력
	- `$ uniq {filename}`
	- `$ cat {filename} | uniq`

- 정렬 후 출력
	- `$ sort {filename}`
	- `$ cat {filename} | uniq`

- 정렬과 중복 동시 적용 후 출력
	- `$ sort -u {filename}`
	- `$ cat {filename} | sort -u`
	- `sort | uniq`도 가능하지만, `sort -u`가 성능면에서 우월하다.

- `$ wc -l {filename}`
	- 특정 파일의 라인 수를 출력하는 쉘 명령어

## 쉘에서 jq로 JSON 메시지 다루기
- jq is command-line JSON processor.
- 공식홈페이지: https://stedolan.github.io/jq/
- kafka record가 json 형식으로 관리될 때, kafkacat과 jq의 조합이 유용하다.
- json 형식의 stdout이 처리대상이므로, cat, echo 명령어 등과 함께 유용하다.

- 설치: `$ sudo apt install jq`

- 조건부 출력 예제
	- `$ kafkacat ~~ -q -e | jq`
		- json line의 stdout을 사람이 보기 편하게 시각화하여 출력한다.

	- `$ kafkacat ~~ -q -e | jq '.'`
		- 위 명령어처럼 jq만 쓴 것과 동일한 효과
		- 따옴표안에는 조건문이 들어간다.
		- '.' (dot) 표현은 '현재까지 정제되어 출력예정인 내용'이라고 보면 된다.
		- 따옴표 안에서 '|' (pipe)와 함께 추가조건을 쓸 수 있다.
		- 다음 예제를 보면 '.'과 '|'의 쓰임새를 이해할 수 있다.

	- `$ kafkacat ~~ -q -e | jq '.RegDate'`
		- RegDate의 value들만 출력한다.
		- RegDate는 데이터의 시간 필드 예시다. (value가 unix timestamp로 표현되는 json key)

	- `$ kafkacat ~~ -q -e | jq 'select(.RegDate>=1665500400000)'`
		- json 리스트에서 RegDate의 값이 1665500400000 이상인 항목만 출력

	- `$ kafkacat ~~ -q -e | jq 'select((.RegDate >= 1664809200000) and (.RegDate < 1664895600000))`
		- RegDate 범위 조건이 여러개인 경우 and를 사용 가능

	- `$ kafkacat ~~ -q -e | jq '.RegDate | (. / 1000 | strflocaltime("%F %T.")) + "00\(.%1000)"[-3:]'`
		- unix timestamp를 DATETIME 형식으로 변환하여 RegDate의 value 목록 출력

	- `$ kafkacat ~~ -q -e | jq 'select((.RegDate >= 1664809200000) and (.RegDate < 1664895600000)) | .RegDate | (. / 1000 | strflocaltime("%F %T.")) + "00\(.%1000)"[-3:]'`
		- DATETIME으로 변환과 시간 범위 지정을 둘다 적용한 예제