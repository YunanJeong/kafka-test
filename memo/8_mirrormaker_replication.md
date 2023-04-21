# 미러메이커 내용 및 테스트

# Kafka 복제 도구 요약
## MM(미러메이커 구버전)
- Apache Kafka에 포함되는 오픈소스 (`bin/kafka-mirror-maker`)
- 3버전대에서 deprecated, 4버전대부터 완전삭제
- 3버전대 Kafka에서 legacy MM1(`bin/kafka-mirror-maker`) 실행 가능
- connect 미사용(consumer + producer로 단순 구현됨)
- [버전 호환성 낮음](https://stackoverflow.com/questions/37864543/kafka-mirrormaker-from-older-version-to-newer-version)
- 동일버전 Kafka 간 미러링이 아니면 호환성 이슈 종종 발생
## MM2(미러메이커 신버전)
- Apache Kafka에 포함되는 오픈소스
- Kafka 2.4 버전부터 지원
- Kafka 3.5.0 버전부터 Exactly-once semantics 지원 (230420 현재 미출시)
- Connector로 제공됨 (Kafka 설치시 기본탑재)
	- MirrorSourceConnector
	- MirrorSinkConnector
	- MirrorCheckpointConnector
	- MirrorHeartBeatConnector
- standalone 모드
	- kafka에 포함된 실행파일(`bin/connect-mirror-maker`)과 properties설정파일로 실행함
	- 독립 프로세스로 connect worker 실행됨
	- `connect-standalone.sh`를 사용하는 것은 아니다.
- distributed 모드
	- `connect-dstributed.sh`로 일반적인 connect를 켜둔 상태에서 REST api로 필요한 커넥터들을 실행함
- 복제 정책
	- MM2 커넥터에서 `LegacyReplicationPolicy`를 설정하면 1버전 미만의 구버전 호환도 가능하다고 함
## Replicator
-  [Confluent Enterprise License 필요](https://docs.confluent.io/platform/current/multi-dc-deployments/replicator/index.html#compatibility) 
- Connector 형태로 제공됨
- Confluent Hub에는 다음과 같이 표기되어 있음
	- Confluent Software Evaluation License
	- 평가 및 테스트용으로 무료가능
	- 상용, 운영환경배포는 허가되지 않음
---
# MirroMaker1 Example: Old to Latest Cluster
매우 오래된 Kafka에서 최신 Kafka로 데이터 복제하기
- 소스 클러스터가 2.4 이전 버전이면 MM1을 써야함
- 목적지 클러스터는 topic 자동생성 옵션 허용 필요
- 일반적으로 최신 Kafka(3.*)에서 제공된 legacy MM1 사용권장
- MirrorMaker 실행 방법
    - 명령어
	```
	bin/kafka-mirror-maker --consumer.config {consumer설정파일} --producer.config {producer설정파일} --whitelist {Java정규표현}
	```
	- consumer, producer 설정파일
		- Kafka 버전따라 구성값 다를 수 있음
		- consumer에 `auto.offset.reset=earliest` 속성이 있으면, MM1이 재실행되었을 때 중단시점부터 데이터를 복제함. 이 속성이 없으면 항상 최신 데이터만 복제함.

	- `--whitelist`: 조건에 맞는 topic 복제
	- `--blacklist`:  조건에 맞는 topic 제외하고 모든 topic 복제
		- ".*"은 빈문자열("")을 포함해서 모든 문자열을 의미. 이거 쓰면 가끔 비정상 작동함.
		- ".+"은 빈문자열("")을 제외하고 모든 문자열을 의미
		```
		# 예: 모든 토픽 미러링
		./bin/kafka-mirror-maker.sh --consumer.config ./config/consumer.properties --producer.config ./config/producer.properties --whitelist ".+"

		# 예: __로 시작하는 topic 빼고 모든 topic 미러링
		./bin/kafka-mirror-maker.sh --consumer.config ./config/consumer.properties --producer.config ./config/producer.properties --blacklist "__*"
		```

## 0.9 => 3.2 (Confluent 7.2) 테스트 
- 0.9Kafka의 MM1을 사용한다.
    - 3.2Kafka의 legacy MM1 사용시 연결 실패
    - 3.2Kafka가 있는 서버에서 0.9Kafka 파일을 다운로드받아 MM1을 실행해도 된다.
- 참고
	- 0.9Kafka는 Java 8 필요 (Java 11 이상 사용시 에러)
	- 0.9Kafka는 topic조회, 등록, Consume 등 대부분 기능에 zookeeeper IP:Port로 접근해야 한다.
	- 0.9Kafka부터 connect 개념이 생겼으나, MM2나 Replicator 호환성 보장은 어렵다.

## 1.0 => 3.2 (Confluent 7.2) 테스트
- 3.2Kafka의 legacy MM1을 사용한다.
    - 1.0Kafka의 MM1 사용시 연결은 되지만, offset처리가 비정상 동작
    - consumer.properties에 `auto.offset.reset=earliest` 속성을 추가했음에도 적용되지 않음 (미러메이커 재실행시, 중단된 동안 복제되지않은 데이터를 무시하고 계속 최신 데이터만 가져와버림)
- 참고
	- 1버전부터 zookeeper가 아닌 broker(bootstrap.servers) 연결정보로 Consume을 수행한다.
