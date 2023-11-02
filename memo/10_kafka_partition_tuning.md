# How to tune the number of partitions

권장사항은 있으나 정답은 없고, 그 때 그 때 다르다.

- [관련 confluet blog 글](https://www.confluent.io/blog/how-choose-number-topics-partitions-kafka-cluster/)
- 클러스터 내 모든 파티션들의 합: 최대 2000개 까지 권장
- 파티션 당 처리량이 10MB/s이 되도록 개수 설정

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

## 저장될 때

- 파티션 개수만큼 분할되어 각 브로커에 분산저장된다.
