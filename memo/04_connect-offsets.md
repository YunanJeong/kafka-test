# connect-offsets

## offset

- 일반적으로 데이터 스트림, 파일 등을 읽을 때 현재 위치를 나타낼 때 사용
- 각 메시지마다 offset넘버를 가지고 있고, 현재 어디까지 읽었는지 offset을 별도저장하는 곳이 있음.
  - Kafka의 경우
  - sink connector: __consumer_offsets
  - src connector: connect-offsets
- 일반적으로 offset: 5 라고 기록되어있으면
  - 5번부터 읽을 차례: O
  - 4번까지 읽음: O
  - 5번까지 읽음: X
  - `Completed until 5`: O
    - 번역에 주의한다.
    - 5번 `전 까지(until)`읽었으니까, 이제 5번부터 읽을 차례라는 의미다.
- offset은 partition마다 따로 관리된다. (topic 별이 아님)

## Sink Connector를 위한 offset 다루기

- Sink Connector는 Consumer이므로, broker에서 일반적인 offset으로 취급, 관리된다.
- offset
  - Consumer가 어떤 topic에 대해 `몇 번째 데이터까지 읽었는지(consume)`, `Broker side에 표기(commit)`해두는 것이다.
  - topic 별, consumer group 별, partition 별로 기록 된다.
  - offset정보의 실제저장경로는 `server.properties의 log.dir 설정경로(kafka-logs)`이다.
  - topic 삭제시 관련 offset도 삭제된다.

### Sink Connector의 offset 재설정

- 일반적인 consumer의 offset 제어와 동일 (`__consumer_offsets`의 데이터를 변경)

```sh
# 설정 전 커넥터 중단

# 특정 커넥터의 오프셋 확인
## (conect-your-connector-name은 자동생성된 consumer group의 이름이다.)
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group connect-your-connector-name --describe

# 특정 오프셋으로 오프셋 재설정
## (e.g. offset이 12345번인 Record부터 읽을 차례라고 지정)
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group connect-your-connector-name --reset-offsets --to-offset 12345 --topic your_topic --execute

# 설정 후 커넥터 재실행
```

## Source connector를 위한 connect-offsets 다루기

- Source Connector는 Producer이기 때문에 Kafka의 일반 offset(__consumer_offsets)과는 별도로 관리된다.
- Source Connector의 offset은 connect-offsets라는 별도 Topic에 저장된다. Source Connector가 `몇 번째 데이터까지 Broker로 Push했는지(produce)`, `Broker의 Topic 'connect-offsets'에 표기`해두는 것이다.
- **Source Connector는 `connect-offsets에서 최신 offset의 Record만 참조`하여, 자신이 어디까지 데이터를 읽었는지 판단한다.**

### connect-offsets의 Record 구조

- Headers: 파티션 넘버, 오프셋 넘버, ...
- Body:
  - key: 커넥터 이름
  - value: 어느 데이터까지 읽었는지 표기 (jdbc의 경우 incrementing key, timestamp key가 저장됨)

### Source Connector의 offset 유지 방법

- 같은 커넥터명으로 삭제, 수정, 등록
- 단, JDBC Source Connector에서는 커넥터명이 동일하더라도 대상 DB, Table이 바뀌면 offset이 유지되지 않는다. 개별 대상마다 offset이 따로 관리되어야 하기 때문.

### Source Connector의 offset 초기화 방법 [[1]](https://rmoff.net/2019/08/15/reset-kafka-connect-source-connector-offsets/) [[2]](https://soojong.tistory.com/entry/Source-Connector-Offset-%EC%B4%88%EA%B8%B0%ED%99%94-%ED%95%98%EA%B8%B0)

#### 1. 다른 커넥터명으로 새로 등록

- 이 경우, 기존 커넥터명으로 저장된 offset은 connect-offsets에 남아있는데, 언제든지 기존 커넥터명을 다시 사용한다면 offset을 이어갈 수 있다.

#### 2. 또는 connect-offsets에 새로운 값을 입력

## connect-offsets 수정시 자주 쓰는 커맨드

### 1. 커넥터 이름 별 offset이 저장되는 Partiton 넘버 찾기

```sh
kafkacat -b localhost:9092 -t connect-offsets -e -q -f'Key:%k Partitions: %p \n' | sort -u
```

```sh
Key:["jdbc_src_1",{"query":"query"}]    Partitions: 5
Key:["jdbc_src_2",{"query":"query"}]    Partitions: 14
Key:["jdbc_src_3",{"query":"query"}]    Partitions: 5
Key:["jdbc_src_4",{"query":"query"}]    Partitions: 14
Key:["jdbc_src_5",{"query":"query"}]    Partitions: 17
Key:["jdbc_src_6",{"query":"query"}]    Partitions: 4
Key:["jdbc_src_7",{"query":"query"}]    Partitions: 12
```

- 처음 partition이 할당되면 그 커넥터는 항상 그 파티션에 offset을 기록한다.
- e.g. Source Connector "jdbc_src_1"는 항상 5번 partition에 offset을 기록한다.
- e.g. Source Connector "jdbc_src_2"는 항상 14번 partition에 offset을 기록한다.

### 2. 다음 커맨드처럼 json형식으로 출력되도록하여 jq를 쓸 수도 있다.

```sh
kafkacat -b localhost:9092 -t connect-offsets -e -q -f'{"Key": %k , "Payload": %s, "Partition": %p,  "Offset": %o }\n'  | jq
```

```txt
- -f: 문자열 포맷을 지정해서 출력가능하게 해준다.
- %p: Partition넘버 (Record Headers)
- %o: offset넘버 (Record Headers)
- %k: Key (Record Body에서 Key부분을 가져온다)
- %s: PayLoad (Record Body에서 Value부분을 가져온다) jdbc Source Connector의 경우, value자리에 incrementing key 또는 timestamp key 값이 입력된다. bulk모드일때는 해당 값이 비어있으므로 위 커맨드처럼 문자열 포맷을 기술하면 json이 깨진다. (jq사용시 주의)
```

### 3. Key-value 포맷 및 내용 확인

```sh
kafkacat -b localhost:9092 -t connect-offsets -e -q -K###
```

### 4. 원하는 Key-value 입력해서 produce하여 offset 조작

- `echo '["{connector_name}", {"query":"query"}]###' | kafkacat -b localhost:9092 -t connect-offsets -P -Z -K### -p {partition}`
- Record의 Body에 해당하는 Key-Value쌍만 직접 새로 입력하는 것이다. Record의 Headers는 자동생성되는 부분이니 헷갈리지 말자!
- 새로운 Record가 connect-offsets의 partition에 등록될 때, Record의 Headers에는 해당 Partition넘버, 최신 Offset넘버 등이 기록된다.

- 아래 예시는 JDBC conenctor가 어디까지 처리했는지에 대한 정보을 수정하는 것이다.
  - Connector는 항상 최신 offset을 가진 Record만 참조하여 어디까지 처리했는지 판단한다. 따라서 새로운 key-value를 1개만 넣어줘도 Connector가 다음 처리할 데이터순서가 바뀐다.
  - 이는 데이터 파이프라인에서 누락이슈 등 발생시 재작업할 때 유용할 수 있다.

```sh
# jdbc_src_1 커넥터는 369034번 데이터까지 읽은 것으로 수정
echo '["jdbc_src_1",{"query":"query"}]#{"incrementing":369034}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 5

# jdbc_src_2 커넥터는 144617150번 데이터까지 읽은 것으로 수정
echo '["jdbc_src_2",{"query":"query"}]#{"incrementing":144617150}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 14

# jdbc_src_3 커넥터는 1669701595817번 데이터까지 읽은 것으로 수정
echo '["jdbc_src_3",{"query":"query"}]#{"timestamp_nanos":817000000,"timestamp":1669701595817}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 5
```
