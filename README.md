# kafka-test
kafka-test

## 디렉토리
```
├── 0_kafka-broker-basic
├── 1_kafka-broker-connect-basic
├── 2_kafka-broker-connect-systemd
├── 3_kafka-jdbc-connector-test
├── 4_kafka-ksql-service
├── 5_confluent-community-archive
├── 6_confluent-community-package
├── LICENSE
├── README.md
├── basic-instance
├── memo
├── py-connect-examples
├── py-connect-util
├── py-kafka-packages
└── test-db-broker-s3
```

## 봐야할 내용
1. kafka 기본
2. CDC, CT 방식중 CT 방식 먼저
3. JDBC 소스커넥터로 db->kafka로 데이터 옮기는 구조 만들기
=> 클러스터 만들지말고 우선 노드 1개로 빠르게 세팅 해보기
4. 이후 클러스터 구성해보기

## Record - Kafka Message Structure
- kafka에서 가장 작은 메시지 단위는 Record라고 부른다.
	- Record = Message = Event = Data = log 1줄 이라고 보면 된다.
- 한 Record 안에는 Headers, key, value가 들어있다.
	- 이 중 Headers에는 topic, partition, timestamp 정보가 있으며, MetaData라고 보면된다.
	- key, value는 일반적으로 Body 또는 Business Relevant Data 라고 표현되는 부분이다. (원본 데이터 내용)

- [참고 그림](https://www.google.com/search?q=kafka+record+timestapme&tbm=isch&ved=2ahUKEwib6f2Lm4L6AhXPZ94KHWiqBJ0Q2-cCegQIABAA&oq=kafka+record+timestapme&gs_lcp=CgNpbWcQAzoECCMQJzoECAAQEzoGCAAQHhATOgUIABCABDoECAAQHjoECAAQGFDQB1iRKWD3LWgAcAB4AIABcYgB_BqSAQUxNC4yMJgBAKABAaoBC2d3cy13aXotaW1nwAEB&sclient=img&ei=ZU8YY9uiIs_P-Qbo1JLoCQ&bih=969&biw=1920&rlz=1C1GCEA_enKR959KR967#imgrc=0ffhDAgddKBNRM)


## 설치관련
[라이센스 자세한 정리](https://github.com/YunanJeong/kafka-test/blob/main/memo/memo_kafka_license.md)
[설치방법 및 관련 라이센스](https://github.com/YunanJeong/kafka-test/blob/main/memo/memo_kafka_install.md)

## How to Analyze and Manage Kafka Messages
- [kafkacat과 jq, 기타 필수 쉘 명령어 사용법](https://github.com/YunanJeong/kafka-test/blob/main/memo/memo_kafkacat_and_jq.md)
