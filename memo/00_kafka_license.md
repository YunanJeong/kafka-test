# Kafka 라이센스 정리

## 결론

- 개인은 Confluent Platform의 `Confluent Community License`를 무료 이용가능하다.
- 회사는 Confluent Platform의 `Confluent Community License`를 무료 이용가능하다.
  - 단, Confluent Platform을 활용하여 Confluent사의 경쟁가능성있는 제품을 만들면 안된다. (e.g. 클라우드 서비스(SaaS,PaaS,...))
- Confluent Platform 없이 Apache Kafka는 무료 이용가능하다.
- 그러나, 장기적으로 ksql 등 추가기능을 쓰려면 Confluent Platform으로 Apache Kafka의 초기 구성을 잡는게 편할 수 있다.

## Apache Kafka (`Apache 2.0 License`)

- 아파치재단(ASF)에서 관리하는 오픈소스
- ASF는 개인, 기업 등이 일종의 후원or 자원봉사 개념으로 소프트웨어를 기여하는 곳이다.
- Confluent 기업도 ASF를 통해 Apache Kafka를 관리하는 주체이다.

## Confluent Platform

- Confluent 회사에서 제공하는 Apache Kafka의 배포판
  - Apache Kafka를 그대로 포함하며 활용성을 높이기 위한 기능이 추가됨
- 아파치 재단과 별개로 Confluent 사에서 제공하며, 독자 라이센스 정책 사용
- "Confluent Platform"이라고 해서 꼭 유료 SaaS를 의미하는 것이 아니다. 배포판을 칭하는 것에 가깝다.
  - 이를테면 Confluent Hub 웹사이트에서 제공하는 플러그인들은 각각 라이센스 및 지원환경 여부를 표기하는데 아래와 같다.
  - Self Hosted: Apache Kafka를 로컬 설치
  - Confluent Platform(Self-Managed): Confluent platform을 로컬설치
  - Confluent Cloud(Full-Managed): Confluent SaaS
- 특히, **Confluent Platform에서 무료 사용가능하면서, Self Hosted에서는 사용금지인 플러그인들이 있으니 주의**하자.
  - (e.g. Confluent 전용 Connect SMT 플러그인들)
  - **자바 jar파일로 제공되기 때문에, 기술적으로 Self Hosted(Apache Kafka)에서 호환될 수도 있으나, 라이센스 정책상 사용 금지**이기 때문

### `Confluent Community License`

- **★ Commercial Use 가능**
- 단 한 가지 예외사항

  ```txt
  Under the Confluent Community License, you can access the source code and modify or redistribute it; there is only one thing you cannot do, and that is use it to make a competing SaaS offering
  ```

  - Confluent의 제품과 "경쟁될 수 있는" SaaS(Paas,Iaas) 서비스를 만드는 일에 사용되면 안된다.
    - e.g. confluent의 ksqldb제품과 경쟁하기 위해 ksqldb 소스를 사용한다 => 라이센스 위반
    - e.g. AWS 등 클라우드 기업이 Confluent Community License의 제품으로 Managed Kafka Service를 만들어 제공한다 => 라이센스 위반
  - 이 제한 때문에 Community License에 해당하는 제품은 공식적으로는 "Open-source"가 아니라 "Source-available"이라고 표현된다.
  - 따라서, 어지간하면 회사에서 써도 된다. 헷갈리는 부분이 있다면 참고자료의 FAQ링크를 참조하자. 매우 잘 설명되어 있다.

### `Confluent Enterprise License`

- Confluent Platform 유료 서비스

### `Developer License`

- non-production 기준으로 전체 상용기능을 무기한 사용해볼 수 있음
- 1 클러스터에 1 브로커만 사용가능
  - 브로커 1개만 가진 클러스터를 여러 개 운용하는 것은 가능
  - 클러스터에 브로커 1개를 더 추가하는 즉시 평가판으로 전환

  ```txt
  Adding a broker starts a trial license that expires in 30 days. You cannot revert from a trial back to a developer license.
  ```
  
### `Trial (Evaluation) License`

- 30일 평가판

## 참고자료

- [Confluent Community License FAQ](https://www.confluent.io/confluent-community-license-faq/)
  - Confluent 사의 각 제품이 어떤 라이센스에 해당하는지 정리된 표

- [Confluent 공식문서의 라이센스 타입 설명](https://docs.confluent.io/platform/current/installation/license.html#license-types)

- [라이센스 관련 토론 레딧](https://www.reddit.com/r/apachekafka/comments/u35gxe/licensing_kafka/)

- [Install Confluent Platform using ZIP and TAR Archives](https://docs.confluent.io/platform/current/installation/installing_cp/zip-tar.html#configure-cp)
  - **Confluent Platform using only Confluent Community components** 항목이 `Confluent Community License`에 해당한다.
