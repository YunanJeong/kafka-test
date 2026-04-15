# Kafka Connect Offset Control

Kafka Connect JDBC Source Connector의 오프셋을 시간 기준으로 수동 제어하기 위한 도구 모음입니다.

## 개요

이 도구는 특정 시점부터 데이터를 재수집하기 위해 Kafka Connect의 오프셋을 조작할 수 있도록 합니다. 주로 데이터 복구, 재처리, 특정 시점 이후 데이터 동기화 등의 목적으로 사용됩니다.

## 주요 기능

- 여러 JDBC Source Connector의 설정 일괄 파싱
- 시간 기준으로 각 DB에서 적절한 ID 조회
- Kafka Connect 오프셋 형식으로 변환
- 누락 방지를 위한 안전한 ID 선택 로직

## 워크플로우

```
Kafka Connect API
      ↓
[0_get_connector_list.sh]
      ↓
tmp/con_list.json
      ↓
[1_get_timebase_id_from_dbs.sh] → MySQL 쿼리
      ↓
tmp/id_list.csv
      ↓
[2_make_kv_offsets_from_id_list.sh]
      ↓
tmp/offsets_to_inject.txt (최종 오프셋 파일)
```

## 파일 구조

```
connect-offset-control/
├── config_tpl.yaml                      # 커넥터 설정 템플릿 (참고용)
├── 0_get_connector_list.sh              # 1단계: 커넥터 정보 조회
├── 1_get_timebase_id_from_dbs.sh        # 2단계: 시간 기준 ID 조회
├── 2_make_kv_offsets_from_id_list.sh    # 3단계: 오프셋 생성
└── tmp/
    ├── con_list.json                    # 조회된 커넥터 목록 (JSON Lines)
    ├── id_list.csv                      # 조회된 ID 목록
    └── offsets_to_inject.txt            # 최종 오프셋 (주입용)
```

## 스크립트 상세 설명

### 0_get_connector_list.sh

**역할:** Kafka Connect REST API에서 실행 중인 JDBC Source Connector 정보를 조회하여 `con_list.json` 생성

**입력:**
- Kafka Connect REST API (http://localhost:8083/connectors)

**출력:**
- `tmp/con_list.json`: JSON Lines 형식 (name, url, catalog, user, password)

**출력 형식:**
```json
{"name":"example-connector-001","url":"jdbc:mysql://example-db-host-1.internal:3306/example_db_001?useUnicode=true&serverTimezone=UTC","catalog":"example_db_001","user":"sample_user","password":"sample_password"}
```

**실행:**
```bash
./0_get_connector_list.sh
```

**참고:**
- Kafka Connect가 실행 중이어야 합니다
- 기본 포트는 8083입니다

---

### 1_get_timebase_id_from_dbs.sh

**역할:** 각 DB에 접속하여 특정 시간 기준 ID를 조회하고 `id_list.csv` 생성

**입력:**
- `tmp/con_list.json`: 커넥터 정보 (JSON 형식)

**출력:**
- `tmp/id_list.csv`: connector_name, db_name, table_name, serverid, id, formatted_time, priority

**환경변수:**
```bash
TABLE        # 조회할 테이블명 (기본값: default_tablename)
TARGET_TIME  # Unix timestamp (기본값: 1767193200, 2026-01-01)
```

**동작 원리:**
1. **1순위:** 타겟 시간 이후 첫 번째 행을 찾아 `ID - 1` 반환 (누락 방지)
2. **2순위:** 데이터가 없으면 전체 최대 ID 행 반환

**실행:**
```bash
TABLE=log_role_map ./1_get_timebase_id_from_dbs.sh
```

---

### 2_make_kv_offsets_from_id_list.sh

**역할:** `id_list.csv`를 Kafka Connect 오프셋 형식으로 변환

**입력:**
- `tmp/id_list.csv`: 조회된 ID 목록

**출력:**
- `tmp/offsets_to_inject.txt`: Kafka Connect 오프셋 (TSV 형식)

**출력 형식:**
```
["example-connector-001",{"protocol":"1","table":"example_db_001.sample_table"}]	{"incrementing":5496789430263982079}
```

**실행:**
```bash
./2_make_kv_offsets_from_id_list.sh
```

## 사용 예시

### 전체 워크플로우 실행

```bash
# 1단계: 커넥터 정보 조회 (Kafka Connect API)
./0_get_connector_list.sh

# 2단계: 특정 시간 기준 ID 조회 (예: 2026년 1월 1일)
TABLE=sample_table TARGET_TIME=1767193200 ./1_get_timebase_id_from_dbs.sh

# 3단계: 오프셋 생성
./2_make_kv_offsets_from_id_list.sh

# 결과 확인
cat tmp/offsets_to_inject.txt
```

### 오프셋 주입 방법

생성된 `tmp/offsets_to_inject.txt` 파일을 Kafka Connect의 offset 토픽에 주입합니다.

**⚠️ 주의:** Kafka Connect를 **중지한 상태**에서 오프셋을 주입해야 합니다.

#### 방법 1: kcat 사용 (권장)

```bash
# 파이프 사용
cat tmp/offsets_to_inject.txt | kcat -b localhost:9092 -t connect-offsets -P -K $'\t' -Z

# 또는 -l 옵션으로 파일 직접 읽기
kcat -b localhost:9092 -t connect-offsets -P -K $'\t' -l tmp/offsets_to_inject.txt
```

**주요 옵션:** `-P` Producer 모드, `-K $'\t'` Key 구분자(탭), `-Z` 전송 완료 대기, `-l` 파일 읽기

#### 방법 2: kafka-console-producer 사용

```bash
cat tmp/offsets_to_inject.txt | \
  kafka-console-producer \
    --bootstrap-server localhost:9092 \
    --topic connect-offsets \
    --property "parse.key=true" \
    --property "key.separator=\t"
```

## con_list.json 형식

0번 스크립트는 Kafka Connect API에서 다음 형식의 JSON을 생성합니다:

```json
{"name":"example-connector-001","url":"jdbc:mysql://example-db-host-1.internal:3306/example_db_001?useUnicode=true&serverTimezone=UTC","catalog":"example_db_001","user":"sample_user","password":"sample_password"}
{"name":"example-connector-002","url":"jdbc:mysql://example-db-host-2.internal:3306/example_db_002?useUnicode=true&serverTimezone=UTC","catalog":"example_db_002","user":"sample_user","password":"sample_password"}
{"name":"example-connector-003","url":"jdbc:mysql://example-db-host-3.internal:3306/example_db_003?useUnicode=true&serverTimezone=UTC","catalog":"example_db_003","user":"sample_user","password":"sample_password"}
```

각 라인은 하나의 커넥터 정보를 나타냅니다 (JSON Lines 형식).

## 주의사항

1. **데이터 누락 방지**: 1번 스크립트는 타겟 시간 직후의 ID에서 1을 빼서 반환합니다. 이는 중복은 허용하더라도 누락이 발생하지 않도록 하기 위함입니다.

2. **인덱스 고려**: time 컬럼에 인덱스가 없는 경우 쿼리 부하가 클 수 있으므로 주의하세요.

3. **테스트 환경 검증**: 프로덕션 환경에 적용하기 전에 반드시 테스트 환경에서 검증하세요.

4. **백업**: 기존 오프셋을 백업한 후 진행하세요.

## 트러블슈팅

### MySQL 연결 오류
- `con_list.json`의 호스트, 포트, 사용자, 비밀번호가 올바른지 확인
- MySQL 서버 접근 권한 확인

### 빈 결과 파일
- `TABLE` 환경변수가 올바르게 설정되었는지 확인
- `TARGET_TIME`이 데이터 범위 내에 있는지 확인
- 1번 스크립트의 주석 해제하여 실제 MySQL 명령어 실행

### 오프셋 주입 실패
- Kafka Connect가 중지된 상태에서 오프셋을 주입해야 합니다
- offset 토픽의 정확한 이름 확인 (기본: `connect-offsets`)

## 라이선스

내부 사용 목적의 도구입니다.
