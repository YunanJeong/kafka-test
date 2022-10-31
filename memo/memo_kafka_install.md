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

# 아카이브(zip,tar) vs. 패키지(deb) 초기 셋업 비교
- 초기 구성 경로
    - zip 최상위 경로 = deb 설치시 루트경로
    - e.g) 설정파일의 위치는
        - zip 설치시, `{kafka directory}/etc/`
        - deb 설치시, `/etc`
- 서비스 등록
    - 둘 다 서비스 파일이 제공됨
    - zip은 개발자가 파일복사 후 systemd 등록해야 하고,
    - deb는 설치시 서비스등록이 완료됨
    - 특이점은 `etc/systemd/system`이 아니라 아니라  `lib/systemd/system`을 사용함
- 로그경로
    - 서비스 파일의 환경변수(LOG_DIR)에 의해 지정됨 (기본 설정: `/var/log/confluent`)
- AWS_KEY
    - S3 Sink 커넥터 사용시 connect 서비스 파일에 AWS_KEY 관련 환경변수 등록 필요
- confluent cli
    - deb 설치시 dependency 중 하나로 자동 설치 및 셋업 됨
    - zip에는 없음
- File Descriptors 설정
    - 둘 다 broker 서비스 파일에 환경변수 등록으로 설정가능
    - [File Descriptors설정 문서 추천방법](https://docs.confluent.io/platform/current/kafka/deployment.html#file-descriptors-and-mmap)
        - OS단위로 설정. 최소 10만개 권장. 세그먼트 파일 개수 확인하고 엔지니어가 조정.
    - 딱히 deb 패키지 설치한다고 자동설정된다는 언급은 없다.

## 설치완료 후 빠른 실행시 확인해야할 것
- server.properties
	- advertised.listeners에 해당 broker에 해당하는 hostname(또는 ip) 기술
	- log.dirs는 record가 저장되는 장소다.(서버, 시스템 로그를 의미하지 않는다.)
		- 디폴트가 /tmp 로 되어있는데, 이는 os에서 삭제해버릴 수도 있는 경로다. /data를 생성해서 써주자.
- connect-distributed.properties
	- connector plugin 경로 지정
- file descriptor 설정
	- systemd 서비스 실행시, 서비스파일에서 설정해야 함
- s3 sink connector 사용시 AWS KEY
	- 실행환경에서 ~/.aws/credentials 파일만 있으면 됨.
	- systemd 서비스 실행시, 서비스파일에서 설정해야 함
- log4j 설정
	- 카프카의 config 경로에 broker용과 connect용 설정이 별도로 있음
	- systemd 서비스 실행시,
		- 설정 파일에서 stdout을 지우면, syslog에도 로그가 남지 않음
		- 카프카 logs 경로에 남는 로그파일은 syslog(stdout)과 별도로 남음
- [production 급에서 고려할 요소 문서](https://docs.confluent.io/platform/current/kafka/deployment.html#running-ak-in-production)