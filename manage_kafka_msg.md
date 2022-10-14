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

- 정렬 및 중복제거 후 출력
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

- `jq '$filter'`
	- 따옴표 안 문자열을 filter라고 칭한다.
	- jq는 filter를 어떻게 쓰냐에 따라 json을 필터링한다. (how to use jq = jq filter syntax)

- 기초
	- `$ jq '.'`
		- stdin 입력을 받는다. json 문자열을 입력하면, 보기 좋게 출력.
	- `$ jq '.' {jsonfile}`
		- json syntax로 기술된 파일을 보기 좋게 출력
	- `$ cat {jsonfile} | jq` or `$ cat {jsonfile} | jq '.'`
		- json syntax로 기술된 stdout을 보기 좋게 출력
		- pipe(|) 앞 내용은 echo, curl, cat 등 stdout이면 모두 적용된다. json syntax에 맞으면 된다.
		- 이처럼 pipe(|)연산으로 jq를 쓰는 경우가 일반적인 jq 용법이다.
	- `$ cat {jsonfile} | jq -c`
		- 대상 json을 jsonline 형식으로 정리하여 출력

- 다양한 jq 필터링으로 json 조건부 출력하기
	- pipe(|): 따옴표 안에서 추가 필터를 기술할 때 쓴다.
	- dot(.):  필터를 거쳐가면서 '현재까지 정제된 내용'을 의미
	- 다음 예제를 보면 '.'과 '|'의 쓰임새를 이해할 수 있다.

	- `$ kafkacat ~~ -q -e | jq '.RegDate'`
		- RegDate의 value들만 출력한다.
		- RegDate는 데이터의 시간 필드 예시다. (value가 unix timestamp로 표현되는 json key)
		- `.RegDate`는 `.["RegDate"]`의 축약형이다.

	- `$ kafkacat ~~ -q -e | jq 'select(.RegDate>=1665500400000)'`
		- json 리스트에서 RegDate의 값이 1665500400000 이상인 항목만 출력

	- `$ kafkacat ~~ -q -e | jq 'select((.RegDate >= 1664809200000) and (.RegDate < 1664895600000))`
		- RegDate 범위 조건이 여러개인 경우 and를 사용 가능

	- `$ kafkacat ~~ -q -e | jq '.RegDate | (. / 1000 | strflocaltime("%F %T.")) + "00\(.%1000)"[-3:]'`
		- unix timestamp를 DATETIME 형식으로 변환하여 RegDate의 value 목록 출력

	- `$ kafkacat ~~ -q -e | jq 'select((.RegDate >= 1664809200000) and (.RegDate < 1664895600000)) | .RegDate | (. / 1000 | strflocaltime("%F %T.")) + "00\(.%1000)"[-3:]'`
		- DATETIME으로 변환과 시간 범위 지정을 둘다 적용한 예제