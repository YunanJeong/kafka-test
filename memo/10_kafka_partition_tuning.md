# How to tune the number of partitions

아래와 같은 통상적인 권장사항은 있으나 정답은 없고, 그 때 그 때 다르다. 버전마다도 조금씩 다르다.

- 브로커 당 2000~4000개 파티션 (최대 4,000)
- 한 클러스터 내 최대 200,000개 파티션
- 파티션 당 처리량이 10MB/s이 되도록 개수 설정
- [confluent_파티션 개수 선택 요령](https://www.confluent.io/blog/how-choose-number-topics-partitions-kafka-cluster/)
- [confluent_파티션 개수 권장사항](https://www.confluent.io/blog/apache-kafka-supports-200k-partitions-per-cluster/)
- [계산식](https://dattell.com/data-architecture-blog/kafka-optimization-how-many-partitions-are-needed/)

## Consume할 때

- 대상 topic의 파티션 수가 많을수록 처리속도가 빠르다.
- consumer-group 또는 connector의 tasks.max 숫자는 해당 topic의 파티션 수에 맞추는 것이 권장사항

## Produce할 때

- 대상 topic의 파티션 수가 많을수록 처리속도가 느려진다.
  - 파티션 수가 여러 개면 각 파티션에 record를 분배할 때 연산량 및 지연시간 발생
    - Producer가 해당 topic의 파티션 정보를 알아야 하므로, Broker에게 메타데이터를 요청해야 한다.
    - 이는 네트워크지연과 처리속도에서 불리해짐
  - 파티션 수가 1개면 직렬이라 처리속도는 빠르다.
- 대상 topic의 파티션 수가 많을수록 안정성이 좋아진다.
  - 분산처리가 되므로 일부 파티션의 장애나 과부하가 다른 파티션으로 전파되지 않음
  - 대규모 데이터 처리시에 적합

## 전체적으로

- 대상 topic의 파티션 수가 많을수록, Kafka Client의 메모리 사용량이 증가
- 대상 topic의 파티션 수가 많을수록 end-to-end latency 증가 (Produce->broker->Consumer)
  - consume 때만 빠르고, 전반적으로 파티션마다 과정이 추가되어서 그런듯.

## 저장될 때

- 파티션 개수만큼 분할되어 각 브로커에 분산저장된다.
