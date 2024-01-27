# 카프카 파티션 수 튜닝 요령

- 정답은 없으나 결국은 특정 값을 설정해야 한다.
- 빠른 설정을 위해 구체적인 방법과 이유를 여기에 기술한다.
- 신규 생성 토픽의 default 파티션 수는 다음과 같이 설정할 수 있다.

```server.properties
# server.properties에서 신규 생성 토픽의 파티션 수를 6으로 지정하는 예시
num.partitions=6
```

## 토픽 당 파티션 개수 (`첫 구축시 최우선 고려사항`)

```sh
- 소규모 클러스터(6개 미만): 브로커 수의 2배
- 대규모 클러스터(12개 이상): 브로커 수와 동일
```

- 한 토픽은 파티션 단위로 각 브로커에 분산저장되는데, 클러스터 `각 노드의 스토리지를 균형있게 사용`하기 위함
- 소규모에서 2배인 이유는 다음 케이스를 대응하기 위함
  - 노드 수도 적고, 토픽 수도 적으면 분산 효과가 떨어질 수 있음
  - 향후 스케일아웃 대비
- 클러스터에서 소규모, 대규모는 통상 10개 전후로 구분하여 칭함
- [[참고]](https://dev.to/jeden/notes-on-kafka-partition-count-and-replication-factor-5dck)

## 처리량 한계 고려

```sh
파티션 당 10MB/s 한도
```

- 메가비트 아니다. 메가바이트다.
- 권장 한계값이다. 이 값보다 낮으면 자원낭비지만, 높으면 안정성이 떨어진다.
- [처리량으로 최적화](https://dattell.com/data-architecture-blog/kafka-optimization-how-many-partitions-are-needed/)

## 클러스터 or 브로커 당 파티션 개수 한도

```sh
- 브로커 당 2000~4000개 활성화된 파티션 (최대 4,000)
- 한 클러스터 내 최대 200,000개 파티션
```

- 버전마다 약간씩 다름
- 권장 한계값이다. 이 값보다 낮으면 자원낭비지만, 높으면 안정성이 떨어진다.
- 토픽 당 파티션 수가 아니다. 클러스터 내 모든 활성화된 파티션 수를 따져보는 것이다.
- [Confluent: Apache Kafka Supports 200K Partitions Per Cluster](https://www.confluent.io/blog/apache-kafka-supports-200k-partitions-per-cluster/)

## 레이턴시를 고려하여 브로커 당 파티션 개수 제한하기

- [Confluent: How to Choose the Number of Topics/Partitions in a Kafka Cluster?](https://www.confluent.io/blog/how-choose-number-topics-partitions-kafka-cluster/)

## 파티션 수 증감에 따른 영향

### 저장될 때

- 파티션 개수만큼 분할되어 각 브로커에 분산저장된다.

### Consume할 때

- 대상 topic의 파티션 수가 많을수록 처리속도가 빠르다.
- consumer-group 또는 connector의 tasks.max 숫자는 해당 topic의 파티션 수에 맞추는 것이 권장사항

### Produce할 때

- 대상 topic의 파티션 수가 많을수록 처리속도가 느려진다.
  - 파티션 수가 여러 개면 각 파티션에 record를 분배할 때 연산량 및 지연시간 발생
    - Producer가 해당 topic의 파티션 정보를 알아야 하므로, Broker에게 메타데이터를 요청해야 한다.
    - 이는 네트워크지연과 처리속도에서 불리해짐
  - 파티션 수가 1개면 직렬이라 처리속도는 빠르다.
- 대상 topic의 파티션 수가 많을수록 안정성이 좋아진다.
  - 분산처리가 되므로 일부 파티션의 장애나 과부하가 다른 파티션으로 전파되지 않음
  - 대규모 데이터 처리시에 적합

### 전체적으로

- 일반적으로 Kafka 클러스터에 파티션이 많을수록 처리량이 높아짐
- But, 파티션이 너무 많으면 가용성과 latency면에서 악영향
- 대상 topic의 파티션 수가 많을수록, Kafka Client의 메모리 사용량이 증가
- 대상 topic의 파티션 수가 많을수록 end-to-end latency 증가 (Produce->broker->Consumer)
