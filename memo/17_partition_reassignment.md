# Partition Reassignment(파티션 재할당)

특정 토픽의 파티션, 복제본들을 브로커 간 재분산하는 작업

## 필요한 상황

- 신규 broker 추가시 파티션 분배
  - 신규 topic 생성시 leader partition과 follower partition(replica)들은 각 broker에 균등하게 분배되지만
  - 클러스터에 신규 broker node 추가시, 기존 topic의 partition이 자동으로 신규 broker에 분배되지 않음
  - 이 때 수동 재할당 작업 필요
- `__consumer_offsets`의 replication factor 변경
  - __consumer_offsets의 replication factor는 topic 최초 생성시 broker 설정값(offsets.topic.replication.factor)에 따르고, 생성 이후엔 변경 불가
  - 이미 운영 중인 서비스의 경우 __consumer_offset을 지우고 신규생성할 수 없으므로 수동 변경이 필요

## 재할당 방법

- kafka bin파일중, `kafka-reassgin-partitions.sh`를 사용
- 이 스크립트는 JSON 형식의 재할당 계획 파일(reassignment.json)을 입력받아 실행한다.
- 재할당 계획 JSON에는 다음이 포함된다:
  - 대상 토픽
  - 각 파티션의 replica를 어느 브로커에 둘지
  - (선택적으로) 리더를 어느 브로커로 둘지 등
- 재할당 계획 JSON은 아래와 같이 `kafka-reassign-partitions.sh --generate` 옵션으로 자동 생성할 수 있다. 또는 자동생성된 포맷을 참고하여 직접 json을 작성해도 된다.

## `__consumer_offsets`의 replication factor (1=>3) 변경, 재할당 방법

- broker의 주소는 localhost:9092로 표기
- 모든 파티션의 복제본을 만들면 replication factor도 그에 맞게 수정된 것으로 표기되며 향후 동작도 그렇게 함

### 1. 현 상태 확인

```sh
kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe --topic __consumer_offsets
```

### 2. 대상 토픽 정의(topics.json)

```json
{
  "topics": [
    {"topic": "__consumer_offsets"}
  ],
  "version": 1
}
```

```sh
# 대상토픽 정의파일 생성
cat > topics.json <<EOF
{
  "topics": [
    {"topic": "__consumer_offsets"}
  ],
  "version": 1
}
EOF
```

### 3. 재할당 계획 정의 (reassignment.json)

```sh
# 재할당 계획 생성
kafka-reassign-partitions.sh \
  --bootstrap-server localhost:9092 \
  --topics-to-move-json-file topics.json \
  --broker-list "0,1,2" \
  --generate > reassignment.json

# broker-list는 broker id를 입력해야 함
# 브로커 지정 갯수만큼 replication factor(RF=3)로 인식하여, 계획 json을 생성해줌
# 만약 브로커 3대인데 RF=2이고, 균등 분배하려면 reassigntment.json을 수동작성해야 함
```

### 4. 재할당 실행

```sh
# 재할당 실행 (완료까지 꽤 시간 소요 필요)
kafka-reassign-partitions.sh \
  --bootstrap-server localhost:9092 \
  --reassignment-json-file reassignment.json \
  --execute
```
