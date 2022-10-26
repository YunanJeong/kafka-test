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

- `sort`
	- 정렬하여 출력
		- `$ sort {file}`
		- `$ cat {file} | sort`

	- 정렬 및 중복제거하여 출력
		- `$ sort -u {file}`
		- `$ cat {file} | sort -u`
		- `sort | uniq`도 가능하지만, `sort -u`가 성능면에서 우월하다.

- `uniq`
	- 주의: uniq 명령어만 단독으로 쓰면 순차적으로 나열된 중복라인만 제거된다. 따라서 먼저 sort하는 과정이 필요하다.
	- `$ sort {file} | uniq`
	- `$ cat {file} | sort | uniq`
	- `$ cat {file} | sort | uniq -d`: 중복이 발생한 행만 출력
	- `$ cat {file} | sort | uniq -u`: 중복이 발생하지 않은 행만 출력

- `$ wc -l {file}`
	- 특정 파일의 라인 수를 출력하는 쉘 명령어

## 쉘에서 jq로 JSON 메시지 다루기
- jq is command-line JSON processor.
- 공식홈페이지: https://stedolan.github.io/jq/
- kafka record가 json 형식으로 관리될 때, kafkacat과 jq의 조합이 유용하다.
- json 형식의 stdout이 처리대상이므로, cat, echo 명령어 등과 함께 유용하다.

- 설치: `$ sudo apt install jq`

- `jq '{filter}'`
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

- Kafka에서
	- `kafkacat ~~ -q -e | jq '{filter}'` 와 같이 활용할 수 있다.

- 다양한 jq filtering으로 json 조건부 출력 예제 커맨드

	- pipe(|): 추가 필터를 기술할 때 따옴표 안에서 쓴다.
	- dot(.):  필터를 거쳐가면서 '현재까지 정제된 내용'을 의미
	- 다음 예제를 보면 '.'과 '|'의 쓰임새를 이해할 수 있다.
	- 소괄호(()): 연산의 우선순위를 정한다. dot과 pipe도 괄호에 따라 적용기준이 바뀌므로 이를 활용하면 필터를 쉽게 구성할 수 있다.
	- +, -: 숫자끼리 덧뺄셈, 문자열끼리는 concat, 배열에서는 element 추가 및 제거

	- 예시 sample.json
		- 다음 스키마를 만족하는 json 리스트 파일
		- Date: 데이터의 시간 필드 (unix timestamp)
		- UserNo: 사용자 식별 번호 (정수형)
		- Name: 사용자이름 (문자열)

	- `$ cat sample.json | jq '.Date'`
		- Date의 value들만 출력한다.
		- `.Date`는 `.["Date"]`의 축약형이다.

	- `$ cat sample.json | jq '.Date, .UserNo'`
		- `,`은 개행하여 나열함을 의미한다.
	- `$ cat sample.json | jq '.Date + .UserNo + 123'`
		- 숫자값끼리 더한다.
	- `$ cat sample.json | jq '".Date"'`
		- 쌍따옴표는 문자열이다. 위 예시는 `.Date`라는 문자열 그대로 출력
	- `$ cat sample.json | jq '"\(.Date)"'`
		- `"\()"`: 숫자 필드의 value를 문자열로 변환 후 출력

	- `$ cat sample.json | jq ' "\(.Date)" + "@" + "\(.UserNo)" + "@" + ".Name" + "123" '`
		- 문자열 합치기
		- {DATE}@{UserNo}@{Name}{123} 형식으로 출력

	- `$ cat sample.json | jq 'select(.Date>=1665500400000)'`
		- json 리스트에서 Date의 값이 1665500400000 이상인 항목만 출력
	- `$ cat sample.json | jq 'select((.Date >= 1664809200000) and (.Date < 1664895600000))`
		- Date 범위 조건이 여러개인 경우 and를 사용 가능
	- `$ cat sample.json | jq '.Date | (. / 1000 | strflocaltime("%F %T.")) + "00\(.%1000)"[-3:]'`
		- Date 필드만을 추출하되, unix timestamp를 DATETIME 형식으로 변환하여 출력
		- `strflocaltime`은  timestamp number를 string으로 변환

	- `$ cat sample.json | jq 'select((.Date >= 1664809200000) and (.Date < 1664895600000)) | .Date | (. / 1000 | strflocaltime("%F %T.")) + "00\(.%1000)"[-3:]'`
		- DATETIME으로 변환과 시간 범위 지정을 둘다 적용한 예제

	- `$ cat sample.json | jq '(  select((.Date >= 1664809200000) and (.Date < 1664895600000)) | .Date | (. / 1000 | strflocaltime("%F %T.")) + "00\(.%1000)"[-3:]  ) + "@" +"\(.UserNo)"'`
		- 시간 범위 내 값들을 {DATETIME}@{UserNo} 형태의 string으로 출력

	- 다양한 연산자 참고: https://hbase.tistory.com/m/167