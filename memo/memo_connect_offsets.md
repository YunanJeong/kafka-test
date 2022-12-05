# Sink Connector를 위한 offset 다루기
- Sink Connector는 Consumer이므로, broker에서 일반적인 offset으로 취급, 관리된다.
- offset
    - Consumer가 어떤 topic에 대해 `몇 번째 데이터까지 읽었는지(consume)`, `Broker side에 표기(commit)`해두는 것이다.
    - topic 별, consumer group 별, partition 별로 기록 된다.
    - offset정보의 실제저장경로는 `server.properties의 log.dir 설정경로(kafka-logs)`이다.
    - topic 삭제시 관련 offset도 삭제된다.

# Source connector를 위한 connect_offsets 다루기
- Source Connector는 Producer이기 때문에 Kafka의 일반 offset관리와는 별도 수행된다.
- Source Connector의 offset은 connect_offsets라는 별도 Topic에 저장된다. Source Connector가 `몇 번째 데이터까지 Broker로 Push했는지(produce)`, `Broker의 Topic 'connect_offsets'에 표기`해두는 것이다.
- **Source Connector는 `connect_offsets에서 최신 offset의 Record만 참조`하여, 자신이 어디까지 데이터를 읽었는지 판단한다.**
### connect_offsets의 Record 구조
    - Headers: 파티션 넘버, 오프셋 넘버, ...
    - Body:
        - key: 커넥터 이름
        - value: 어느 데이터까지 읽었는지 표기 (jdbc의 경우 incrementing key, timestamp key가 저장됨)


## Source Connector의 offset 유지 방법
    - 같은 커넥터명으로 삭제, 수정, 등록

## Source Connector의 offset 초기화 방법 [[1]](https://rmoff.net/2019/08/15/reset-kafka-connect-source-connector-offsets/) [[2]](https://soojong.tistory.com/entry/Source-Connector-Offset-%EC%B4%88%EA%B8%B0%ED%99%94-%ED%95%98%EA%B8%B0)
    1. 다른 커넥터명으로 새로 등록
        - 이 경우, 기존 커넥터명으로 저장된 offset은 계속 남아있다!
    2. 또는 connect_offsets에 새로운 값을 입력


## connect_offsets 수정시 자주 쓰는 커맨드
1. 커넥터 이름 별 offset이 저장되는 Partiton 넘버 찾기
- `$ kafkacat -b localhost:9092 -t connect-offsets -e -q -f'Key:%k Partitions: %p \n' | sort -u`
    ```
    Key:["jdbc_src_1",{"query":"query"}]    Partitions: 5
    Key:["jdbc_src_2",{"query":"query"}]    Partitions: 14
    Key:["jdbc_src_3",{"query":"query"}]    Partitions: 5
    Key:["jdbc_src_4",{"query":"query"}]    Partitions: 14
    Key:["jdbc_src_5",{"query":"query"}]    Partitions: 17
    Key:["jdbc_src_6",{"query":"query"}]    Partitions: 4
    Key:["jdbc_src_7",{"query":"query"}]    Partitions: 12
    ```

2. 다음 커맨드처럼 json형식으로 기술해서 jq를 쓸 수도 있다.
    ```
    $ kafkacat -b localhost:9092 -t connect-offsets -e -q -f'{"Key": %k , "Payload": %s, "Partition": %p,  "Offset": %o }\n'  | jq
    ```
    ```
    - f: 문자열
    - %o: offset넘버
    - %k: payload. jdbc Source Connector의 경우, record의 value자리에 incrementing key 또는 timestamp key 값이 입력된다. bulk모드일때는 해당 값이 비어있으므로 json이 위 처럼 쓰면 json이 깨진다.
    ```

3. Key-value 포맷 확인
    - `kafkacat -b localhost:9092 -t connect-offsets -e -q -K###`

4. 원하는 Key-value 입력해서 produce하여 offset 조작
    - `echo '["{connector_name}", {"query":"query"}]###' | kafkacat -b localhost:9092 -t connect-offsets -P -Z -K### -p {partition}`

    ```
    # jdbc_src_1 커넥터는 369034번 데이터까지 읽은 것으로 수정
    echo '["jdbc_src_1",{"query":"query"}]#{"incrementing":369034}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 5

    # jdbc_src_2 커넥터는 144617150번 데이터까지 읽은 것으로 수정
    echo '["jdbc_src_2",{"query":"query"}]#{"incrementing":144617150}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 14

    # jdbc_src_3 커넥터는 1669701595817번 데이터까지 읽은 것으로 수정
    echo '["jdbc_src_3",{"query":"query"}]#{"timestamp_nanos":817000000,"timestamp":1669701595817}' | kafkacat -b localhost:9092 -t connect-offsets -P  -K# -p 5
    ```

