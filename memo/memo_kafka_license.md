# Kafka의 헷갈리는 라이센스 정리

## 결론
- 개인은 Confluent Platform의 `Confluent Community License`를 무료 이용가능하다.
- 회사는 Confluent Confluet Platform의 `Confluent Community License`를 무료 이용가능하다.
    - 단, Confluent Platform을 활용하여 Confluent사의 경쟁 제품을 만들면 안된다. (e.g. 클라우드 서비스(SaaS,PaaS,...))
- Confluent Platform 없이 Apache Kafka는 무료 이용가능하다.
- 그러나, 장기적으로 ksql 등 추가기능을 쓰려면 Confluent Platform으로 Apache Kafka의 초기 구성을 잡는게 편하다.


## 정리
### Apache Kafka (`Apache 2.0 License`)
    - 아파치재단(ASF)에서 관리하는 오픈소스
    - ASF는 개인, 기업 등이 일종의 후원or 자원봉사 개념으로 소프트웨어를 기여하는 곳이다.
    - Confluent 기업도 ASF를 통해 Apache Kafka를 관리하는 주체이다.

### Confluent Platform
    - Apache Kafka 활용성을 높여주는 플랫폼을 의미 (설치시 Apache Kafka가 포함)
    - **아파치 재단과 별개로** Confluent에서 제공하는 플랫폼
    - 독자적인 라이센스 정책을 쓴다.

- `Confluent Community License`
    - **★ Commercial Use 가능**
    - 단 한 가지 예외사항
        - Under the Confluent Community License, you can access the source code and modify or redistribute it; there is **only one thing you cannot do, and that is use it to make a competing SaaS offering**.
        - Confluent의 제품과 "경쟁될 수 있는" SaaS(Paas,Iaas) 서비스를 만드는 일이 아니어야 한다.
        - e.g.) confluent의 ksqldb제품과 경쟁하기 위해 ksqldb 소스를 사용한다 => 라이센스 위반
        - e.g.) AWS에서 Confluent Community License에 해당하는 기능으로 어떤 서비스를 제공한다 => 라이센스 위반
        - 이 제한 때문에 Community License에 해당하는 제품은 공식적으로는 "Open-source"가 아니다.
        - "Source-available"이라고 표현된다.
        - 따라서, 어지간하면 회사에서 써도 된다. 헷갈리는 부분이 있다면 참고자료의 FAQ링크를 참조하자. 매우 잘 설명되어 있다.

- `Confluent Enterprise License`
    - Confluent Platform 유료 서비스

- `Developer License`
    - non-production 기준으로 전체 상용기능을 무기한 사용해볼 수 있음
    - 1 클러스터에 1 브로커만 사용가능
        - 브로커 1개만 가진 클러스터를 여러 개 운용하는 것은 가능
    - Adding a broker starts a trial license that expires in 30 days. You cannot revert from a trial back to a developer license.
        - 브로커를 추가하면 평가판으로 전환된다고 표현되어다.
        - 맥락상 브로커 2개 이상을 가진 클러스터 생성을 의미하는 듯 하다.

- `Trial (Evaluation) License`
    - 30일 평가판


## 참고자료
>- `Confluent Community License FAQ`
>	- ★ kafka와 관련된 세 가지 라이센스 별로 사용가능한 제품범위가 표로 잘 정리되어 있다.
>        - `Apache 2.0 License`, `Confluent Community License`, `Confluent Enterprise License`
>	- https://www.confluent.io/confluent-community-license-faq/

>- Confluent 문서의 Confluent Platform 라이센스 타입
>    - https://docs.confluent.io/platform/current/installation/license.html#license-types

>- 라이센스 관련 토론
>	- https://www.reddit.com/r/apachekafka/comments/u35gxe/licensing_kafka/

>- Confluent 전체 기능 standalone 압축파일 다운로드
>	- https://docs.confluent.io/platform/current/installation/installing_cp/zip-tar.html#configure-cp
>	- **Confluent Platform using only Confluent Community components** 항목이 `Confluent Community License`에 해당한다.