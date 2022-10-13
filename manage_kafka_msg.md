# How to Manage and Analyze Kafka Messages

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

- 정렬 후 출력
	- `$ sort {filename}`
	- `$ cat {filename} | sort`

- 중복제거 후 출력 (사용 비권장)
	- 주의: uniq 명령어만 단독으로 쓰면 순차적으로 나열된 중복라인만 제거해준다. 따라서 먼저 sort하는 과정이 필요하다.
	- `$ uniq {filename}`
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