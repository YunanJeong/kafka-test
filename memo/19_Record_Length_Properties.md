## 컴포넌트 체크포인트 

- 파이프라인 중 하나라도 놓치면 끊길 수 있으므로 잘 체크하자
- Kafka Broker
  - server.properties
  - topic
- Kafka Client (Streams, Connect, ...)
  - producer
  - consumer

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