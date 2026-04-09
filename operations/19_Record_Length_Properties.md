# 단일 메시지(Record) 최대 한도 설정

- 기본 1MB에 맞춰줘 있는데 10MB 등으로 늘릴 시 알아둘 것들 정리

## 컴포넌트 체크포인트 

- 파이프라인 중 하나라도 놓치면 끊길 수 있으므로 잘 체크하자
- Kafka Broker
  - server.properties
  - topic
- Kafka Client (Streams, Connect, ...)
  - producer
  - consumer

## 참고자료

- https://kafka.apache.org/41/configuration/broker-configs/
- https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/ConsumerConfig.html
- https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/producer/ProducerConfig.html
- https://always-kimkim.tistory.com/entry/kafka-operations-settings-concerned-when-the-message-has-more-than-1-mb
- 필수설정(Hard Limit)과 비필수설정(Soft Limit, 성능제어목적)이 있는데, 상당 수 AI가 이 구분을 틀리게 답하므로 반드시 문서 참고하고 테스트할 것

## Hard limit과 Soft limit

### `Produce 과정은 주로 필수옵션(hard limit)` 이라 단일 Record 크기가 설정값보다 크면 `즉시 실패`한다.
### `Replication, Consume의 경우 주로 soft limit`이라 단일 Record 크기가 설정값보다 크더라도, `예외처리해서 진행`은 시켜준다.

- soft limit 옵션은 그럼 왜 설정하나?
- => 처리할 데이터가 많을 때 Record Batch 최대 크기를 조절하여 부하방지하기 위한 목적이 큼. 굳이 실패 상황을 일으키지는 않음

## Hard limit(단일 Record 길이 제한 수정시 필수옵션)

### Broker (server.properties)
```properties
# default 1048588 (1MiB)
message.max.bytes=10485760

# default 104857600 (100MiB)  # default가 100MB에 달하므로 단일 길이 10MB일 땐 수정할 필요없음
socket.request.max.bytes=104857600
```

### Topic

```properties
# default 1048588 (1MiB)
max.message.bytes=10485760
```

### Producer
```properties
# default 1048576 (1MiB)
producer.max.request.size=10485760
```

### Consumer

```
consumer는 hard limit 없음
```

## Soft limit(비필수 설정, 성능제어 목적)

- 1MB 이상의 Record가 자주 발생한다면 설정이 권장되나, 간헐적으로만 발생한다면 설정할 필요 없음

### server.properties

```properties
# broker replication

# replication시 단일 메세지 최대 허용량
# follwer replica가 leader쪽으로 요청해서 데이터를 가져올 때(fetch) 크기 길이 제한 #  (개별 Topic 설정불가, server.properties에서만 설정)
# default 1048576
replica.fetch.max.bytes=10485760

# default 10485760
replica.fetch.response.max.bytes=10485760

# default 65536
replica.socket.receive.buffer.bytes=65536


# broker socket buffers
# default 102400
socket.receive.buffer.bytes=102400

# default 102400
socket.send.buffer.bytes=102400
```

### Producer (producer buffers)

```properties
# default 33554432
producer.buffer.memory=33554432

# default 32768
producer.receive.buffer.bytes=32768

# default 131072
producer.send.buffer.bytes=131072
```

### Consumer (consumer fetch/buffers)

```properties
# consumer가 broker에 fetch 요청 후 응답으로 데이터 받을 때 파티션 당 RecordBatch 총 크기 제한
# default 1048576
consumer.max.partition.fetch.bytes=10485760

# consumer가 broker에 fetch 요청 후 응답으로 데이터 받을 때 RecordBatch 총 크기 제한
# default 52428800
consumer.fetch.max.bytes=52428800

# default 65536
consumer.receive.buffer.bytes=65536

# default 500
consumer.max.poll.records=500
```

## 헷갈리지말 것 메모

### fetch, bytes, size 프로퍼티
- Kafka fetch/bytes/size 속성 대부분 Kafka Application Layer에서 제어하는 값이다.
- 이 값들은 단일 Record를 `쪼개서 전송할 버퍼를 정하는 게 아니다.` (그건 TCP 레벨에서 일어나는 일)
- `Kafka App Level에서 데이터는 항상 RecordBatch`(최소 1개 이상의 Record 묶음) 단위로 전송/반환되며, 크기 관련 속성들은 RecordBatch 처리에 대한 커스터마이징이다.
- Kafka App Level에서 최소 단위는 Record이며 쪼개지지 않는다.
- `TCP 레벨의 제어는 socket, buffer 등의 키워드`가 들어간 프로퍼티에서 볼 수 있다.
- 속성 값이 단일 Record보다 작으면 단일 Record를 쪼개서 맞추는 게 아니라, 전송 실패 or 예외 처리로 통과된다.
  - 전송실패(hard limit) 되는지 예외처리로 통과시켜주는지(soft limit)는 옵션에 따라 다르다.
