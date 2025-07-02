# How to Manage and Analyze Kafka Messages

## kcat(구 kafkacat) 활용

- 이름이 kcat, kafkacat로 혼용되며 배포환경마다 다름
- 공식명은 kcat으로 굳어짐 (Ubuntu24부터 kcat)

```sh
# 설치
sudo apt install kcat
#  -L: List, 메타 정보 조회
#  -b: broker 지정
#  -t: topic 지정
#  -p: partition 지정
#  -q: quiet
#  -e: exit
#  -o: offset
#  -P: Producer Mode  # 내용 입력시 반드시 파이프라인(|)으로 stdin처리 
#  -C: Consumer Mode
```

### kcat 조회

- 예시
  - broker: localhost:9092
  - topic: mytopic
- `$ kcat -b localhost:9092 -L`
  - 해당 브로커의 메타정보를 보여준다.
  - 브로커, 토픽, 파티션 목록을 보여 준다.
- `$ kcat -b localhost:9092 -t mytopic -L`
  - 브로커와 토픽을 지정하고, L옵션을 설정
  - 해당 토픽에 한정해서 메타정보를 보여준다.

### kcat Consume

- `$ kcat -b localhost:9092 -t mytopic`
  - 브로커와 토픽을 지정
  - 기본적으로 Consumer mode로 취급되어 해당 토픽의 Record를 보여준다.
  - `$ kcat -b localhost:9092 -t mytopic -C` 와 동일
  - 지정 토픽이 존재하지 않는 경우, Consume을 수행했을 때
    - kafka 내장 쉘명령어는 해당 빈 토픽을 자동생성하지만,
    - kcat은 자동생성하지 않고 에러를 출력한다.
- `$ kcat -b localhost:9092 -t mytopic -C -q`
  - Consumer Mode에서 q 옵션 사용시, Record 내용만 조회할 수 있다.
  - '새 메시지가 도착했다'라는 출력이 표시되지 않는다.
- `$ kcat -b localhost:9092 -t mytopic -C -e`
  - e 옵션 사용시 마지막 내용까지 출력한 후 대기모드상태에 있지 않고 자동 exit한다.
- `$ kcat -b localhost:9092 -t mytopic -o offset`
  - `$ kcat -b localhost:9092 -t mytopic -o beginning`
    - 처음부터 모든 record 조회(토픽에 쌓인 record가 많으면 최근 새로 업데이트 되는 record만 보이기 때문에 이 옵션이 필요)
  - `$ kcat -b localhost:9092 -t mytopic -o -1000`
    - 최근 1000개 record 조회
  - `$ kcat -b localhost:9092 -t mytopic -p 0 -o 1368 -c 1`
    - '0번 파티션'에서 '1368번 offset'부터 '1개의 record' 조회

### kcat Produce

- `$ kcat -b localhost:9092 -t mytopic -P`
  - 브로커와 토픽을 지정하고, Producer mode로 설정했다.
  - 명령어 입력 후 이어서 쉘에 입력한 내용이 토픽의 Record로 저장된다.
  - 다른 쉘에서 Consumer mode를 열어놓고 실시간으로 확인해볼 수 있다.
  - 지정 토픽이 존재하지 않는 경우, 자동 생성한다.

```sh
# kcat Produce 내용 입력시, stdin 버퍼링으로 인해 처리되지않는 이슈가 잦다.
# kafka 트러블슈팅시 상당히 방해가 된다.
# kcat Produce시에는 """반드시""" 파이프라인(|)을 활용하도록 하자
echo "myRecordMessage" | kcat -b localhost:9092 -t mytopic -P
cat myrecordfile.txt   | kcat -b localhost:9092 -t mytopic -P 
```

## 쉘에서 메시지 관리&분석 하기

아래 명령어들은 모두 라인 단위로 이루어진다. (다른 라인끼리만 비교한다. 같은 라인 내에서 중복, 정렬 처리를 하지 않는다.)

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

## 쉘에서 jq로 JSON stdout 다루기

### jq ([공홈](https://stedolan.github.io/jq/))

- command-line JSON processor
- kafka record가 json 형식이면, kcat과 jq의 조합이 유용
- 설치

  ```sh
  sudo apt install -y jq
  ```

### 기본 커맨드

```sh
# json 형식 입력(stdin)을 보기 좋게 출력
jq '.'

# json 파일을 보기 좋게 출력
jq '.' sample.json

# json 형식 stdout(echo, curl, cat, ...)을 보기 좋게 출력
cat sample.json | jq
cat sample.json | jq '.'

# -c: jsonline 형식으로 출력
cat sample.json | jq -c
```

### jq filter

- 따옴표(`''`) 안에 filter를 기술
- filter에 따라 json이 필터링되어 출력

  ```sh
  jq '{filter}'
  ```

- filter 연산자
  - pipe(`|`)
    - 추가 필터 기술
  - dot(`.`)
    - pipe로 새 필터를 기술할 때, **현재까지 정제된 메시지**를 의미
  - 소괄호(`()`): 연산의 우선순위 지정
    - dot과 pipe도 괄호에 따라 적용순서가 바뀜
  - `+`, `-`
    - 숫자끼리 덧뺄셈
    - 문자열끼리 concat
    - 배열에서는 element 추가 및 제거
  - [기타 jq filter 연산자](https://hbase.tistory.com/m/167)

### 활용 예시

#### 0. 다음 스키마를 가진 topic 데이터를 분석한다고 가정

- Date: 데이터의 시간 필드 (unix timestamp)
- UserNo: 사용자 식별 번호 (정수형)
- Name: 사용자이름 (문자열)

```json
(...)
{"Date": 1694275771, "UserNo": 1, "Name": "myName"}
{"Date": 1694275772, "UserNo": 2, "Name": "myName2"}
{"Date": 1694275773, "UserNo": 3, "Name": "myName3"}
{"Date": 1694275774, "UserNo": 4, "Name": "myName4"}
(...)
```

#### 1. kafka topic 데이터를 파일로 저장

```sh
# kcat에서 -q, -e 옵션을 써줘야, 깔끔한 jsonline 리스트로 파일이 생성된다
kcat -b localhost:9002 -t mytopic -C -q -e > sample.json
```

#### 2. 데이터 분석

```sh
# Date의 value들만 출력
# `.Date`는 `.["Date"]`의 축약형이다.
cat sample.json | jq '.Date'

# `,`은 개행하여 나열함을 의미
cat sample.json | jq '.Date, .UserNo'

# 숫자값끼리 덧셈
cat sample.json | jq '.Date + .UserNo + 123'

# 쌍따옴표는 문자열을 의미
# `.Date`라는 문자열 그대로 출력
cat sample.json | jq '".Date"'

# `"\()"`: 숫자 필드의 value를 문자열로 변환 후 출력
cat sample.json | jq '"\(.Date)"'
```

```sh
# 문자열 합치기
# {DATE}@{UserNo}@{Name}{123} 형식으로 출력
cat sample.json | jq ' "\(.Date)" + "@" + "\(.UserNo)" + "@" + ".Name" + "123" '

# json 리스트에서 Date의 값이 1665500400000 이상인 항목만 출력
cat sample.json | jq 'select(.Date>=1665500400000)'

# Date 범위 조건이 여러개인 경우 and를 사용 가능
cat sample.json | jq 'select((.Date >= 1664809200000) and (.Date < 1664895600000))'

# Date 필드만을 추출하되, unix timestamp를 DATETIME 형식으로 변환하여 출력
# `strflocaltime`:  timestamp number를 string으로 변환하는 함수
cat sample.json | jq '.Date | (. / 1000 | strflocaltime("%F %T.")) + "00\(.%1000)"[-3:]'

# DATETIME으로 변환과 시간 범위 지정을 둘다 적용한 예제
cat sample.json | jq 'select((.Date >= 1664809200000) and (.Date < 1664895600000)) | .Date | (. / 1000 | strflocaltime("%F %T.")) + "00\(.%1000)"[-3:]'

# 시간 범위 내 값들을 {DATETIME}@{UserNo} 형태의 string으로 출력
cat sample.json | jq '(  select((.Date >= 1664809200000) and (.Date < 1664895600000)) | .Date | (. / 1000 | strflocaltime("%F %T.")) + "00\(.%1000)"[-3:]  ) + "@" +"\(.UserNo)"'
```
