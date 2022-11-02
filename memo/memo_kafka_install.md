# 설치 방법에 따른 라이센스
## Apache Kafka 공홈 (Apache Kafka 설치)
- https://kafka.apache.org/quickstart
- Apache 2.0 License

## Confluent 공홈 (Apache Kafka + Confluent Platform 설치)
 https://www.confluent.io/installation/
 첫페이지는 회원가입이 아니다. 귀찮지 않다. 약관 동의를 위해 이름, 메일만 요구한다. 아무거나 입력해도 페이지는 넘어간다. Local, Distributed, Community 로 구분된다. 사이드에 deb/rpm 설치도 있다. 각각 라이센스가 다르니 주의! (FAQ 참고)

### Local
- zip or tar: `Confluent Enterprise License`
- docker:
    - 이미지에 포함된 제품&기능별 라이센스 구분
    - Quick Start를 누르면 Confluent Cloud 페이지로 이동 (Confluent Enterprise License)
### Distributed
- Confluent for Kubernetes: `Confluent Enterprise License`
- Ansible Playbooks: `Apache 2.0 License`

### Community (`Confluent Community License`)
- zip, tar: Community 제품만 있는 로컬파일
- docker:
    - 이미지에 포함된 제품&기능별 라이센스 구분
    - Quick Start를 누르면 가이드 문서로 이동. docker 적용법 확인가능

### Ubuntu DEB
- Community버전과 Enterprise 버전이 나누어져 있음
- Dependency로 각 기능이 나누어져 있고, Community버전 설치시 Community에 해당하는 Depedency deb 패키지들만 설치된다.
- 인터넷 차단망 셋업용 deb파일 추출시 dependency tree가 2~3단계까지 필요하므로 별도 체크할 것
    - 보통 confluent라고 적힌 dependency만 신경 쓰면된다.

### RPM
- CentOS 등에서 패키지 설치

# Confluent Platform의 아카이브(zip,tar) vs. 패키지(deb) 초기 셋업
- 초기 구성 경로
    - zip 최상위 경로 = deb 설치시 루트경로
    - e.g) 설정파일의 위치는
        - zip: `{KAFKA_HOME}/etc/`
        - deb: `/etc`
    - bin실행파일
        - zip: `{KAFKA_HOME}/bin/`
        - deb: `/usr/bin`과 `/bin`에 둘 다 설치됨
        - 참고: Apache Kafka와 달리 sh 파일이 아니라 바이너리 파일이 제공됨
- 로그경로
    - zookeeper, broker, connect
        - zip: `{KAFKA_HOME}/logs/`
        - deb: `/var/log/kafka/`
        - 서비스 파일에서 환경 변수 `LOG_DIR` 등록하여 변경가능
    - ksqldb, schema registry 등 confluent 고유제품들
        - `/var/log/confluent/{제품명}/` (기본 제공 서비스파일에 이미 `LOG_DIR` 등록되어 있음)
        - zip 설치여도 `/var/log/confluent/` 디렉토리는 자동생성
        - 서비스 파일에 `KSQL_LOG4J_OPTS` 환경변수로 log4j 설정파일을 참조해줘야 로그파일 및 syslog 생성함

- 서비스 등록
    - `lib/systemd/system`에서 기본 서비스 파일 제공됨
    - zip: systemd 직접 등록 필요
        - 서비스파일 내 경로관련 값은 모두 root(/)기준으로 기술되어 있음. 해당 부분 수정 필요
    - deb: 설치시 서비스등록 완료. 빠른 실행 정도는 가능하지만, production시 어차피 수정 필요

- ksql 등 실행파일 환경변수 등록
    - zip: 수동등록
    - deb: 설치시 자동등록

- confluent cli
    - zip: 없음
    - deb: dependency 중 하나로 자동 설치 및 셋업
    - 사실상 유료 cloud 서비스에서 클러스터 관리 목적이 크다. 로컬 1노드 기준, `$ confluent local` 커맨드 일부 사용가능



## 설치완료 후 빠른 실행시 확인해야할 것
- server.properties
	- advertised.listeners에 해당 broker에 해당하는 hostname(또는 ip) 기술
	- log.dirs는 record가 저장되는 장소다.(서버, 시스템 로그를 의미하지 않는다.)
		- 디폴트가 `/tmp` 인데, 이는 os에서 주기적으로 삭제할 수 있다. `/data`를 생성해서 써주자.
- connect-distributed.properties
	- connector plugin 경로 지정
- File Descriptors 설정
	- systemd 서비스 실행시, 서비스파일에서 설정해야 함
    - [File Descriptors 값 조정 방법](https://docs.confluent.io/platform/current/kafka/deployment.html#file-descriptors-and-mmap)


- S3 Sink Connector 사용시 AWS KEY
	- 실행환경에서 `~/.aws/credentials` 파일만 있으면 됨.
	- systemd 실행시, connect 서비스 파일에 AWS_KEY 관련 환경변수 등록 필요


- log4j 설정
	- 카프카의 config 경로에 broker용과 connect용 설정이 별도로 있음
	- systemd 서비스 실행시,
		- 설정 파일에서 stdout을 지우면, syslog에도 로그가 남지 않음
		- 카프카 logs 경로에 남는 로그파일은 syslog(stdout)과 별도로 남음
- [production 급에서 고려할 요소 문서](https://docs.confluent.io/platform/current/kafka/deployment.html#running-ak-in-production)