# Kafka Connect JDBC Source Offset Control

Kafka Connect JDBC Source Connector(incrementing 모드)의 오프셋을 특정 시점으로 되돌리기 위한 도구입니다.

데이터 복구, 재처리, 특정 시점 이후 재수집 등의 목적으로 사용합니다.

## 워크플로우

```
[0_print_jdbc_src_connectors.sh]    Kafka Connect API에서 커넥터 정보 조회
               |
               v
     jdbc_src_connectors.jsonl
               |
               v
[1_query_cutoff_ids_by_time.sh]     각 DB에서 특정 시간 기준 cutoff ID 조회
               |
               v
   ${TARGET_TABLE}_cutoff_ids.csv
               |
               v
[2_build_connector_offsets.sh]      cutoff ID를 Kafka Connect offset 형식으로 변환
               |
               v
 ${TARGET_TABLE}_connector_offsets.txt
               |
               v
         kcat / kafka-console-producer로 connect-offsets 토픽에 주입
```

## 사용법

```bash
# 0. 커넥터 정보 조회 (stdout → 파일 리다이렉션)
./0_print_jdbc_src_connectors.sh > /tmp/jdbc_src_connectors.jsonl

# 1. 특정 시간 기준 cutoff ID 조회 (예: 2026-01-01)
TARGET_TABLE=sample TARGET_TIME=1767193200 ./1_query_cutoff_ids_by_time.sh

# 2. offset 메시지 생성
TARGET_TABLE=sample ./2_build_connector_offsets.sh

# 3. 결과 확인
cat /tmp/sample_connector_offsets.txt
```

## 오프셋 주입

**Kafka Connect를 반드시 중지한 상태에서 주입해야 합니다.**

```bash
# kcat 사용 (권장)
cat /tmp/sample_connector_offsets.txt | kcat -b localhost:9092 -t connect-offsets -P -K '\t' -Z

# 또는 kafka-console-producer 사용
cat /tmp/sample_connector_offsets.txt | \
  kafka-console-producer \
    --bootstrap-server localhost:9092 \
    --topic connect-offsets \
    --property "parse.key=true" \
    --property "key.separator=\t"
```

## 파일 구조

```
connect-offset-control/
├── 0_print_jdbc_src_connectors.sh            # Kafka Connect API → 커넥터 목록 (stdout)
├── 1_query_cutoff_ids_by_time.sh             # MySQL 쿼리 → cutoff ID
├── 2_build_connector_offsets.sh              # cutoff ID → offset 메시지
└── $TEMP/
    ├── jdbc_src_connectors.jsonl             # 커넥터 정보 (name, url, catalog, user, password)
    ├── ${TARGET_TABLE}_cutoff_ids.csv        # connector_name, db_name, table_name, serverid, id, time, priority
    └── ${TARGET_TABLE}_connector_offsets.txt # KEY\tVALUE (Kafka Connect offset 형식)
```

## 스크립트 상세

### 0_print_jdbc_src_connectors.sh

Kafka Connect REST API에서 `JdbcSourceConnector` 클래스인 커넥터만 필터링하여 DB 연결 정보를 stdout으로 출력합니다.

| 항목 | 값 |
|------|---|
| 입력 | Kafka Connect REST API (`localhost:8083`) |
| 출력 | stdout (JSON Lines 형식) |

```json
{"name":"my-connector-001","url":"jdbc:mysql://host:3306/db","catalog":"db","user":"user","password":"pw"}
```

### 1_query_cutoff_ids_by_time.sh

각 DB에 접속하여 `time` 컬럼 기준으로 cutoff ID를 조회합니다.

| 항목 | 값 |
|------|---|
| 입력 | `$TEMP/jdbc_src_connectors.jsonl` |
| 출력 | `$TEMP/${TARGET_TABLE}_cutoff_ids.csv` |

**cutoff ID 선택 로직:**

| 우선순위 | 조건 | 반환값 |
|----------|------|--------|
| 1순위 | TARGET_TIME 이후 데이터 존재 | 해당 행의 `id - 1` (누락 방지) |
| 2순위 | TARGET_TIME 이후 데이터 없음 | 테이블 내 최대 ID |

### 2_build_connector_offsets.sh

cutoff ID를 Kafka Connect의 offset 메시지 형식(TSV)으로 변환합니다.

| 항목 | 값 |
|------|---|
| 입력 | `$TEMP/${TARGET_TABLE}_cutoff_ids.csv` |
| 출력 | `$TEMP/${TARGET_TABLE}_connector_offsets.txt` |

```
["connector-name",{"protocol":"1","table":"db.table"}]\t{"incrementing":id}
```

## 환경변수

| 변수 | 설명 | 기본값 | 사용 스크립트 |
|------|------|--------|--------------|
| `TEMP` | 중간 파일 경로 | `/tmp` | 1, 2 |
| `TARGET_TABLE` | 조회 대상 테이블명 | `sample` | 1, 2 |
| `TARGET_TIME` | cutoff 기준 시간 (Unix timestamp) | `1767193200` (2026-01-01) | 1 |

## 주의사항

- **누락 방지**: cutoff ID는 타겟 시간 직후 행의 `id - 1`을 사용합니다. 중복은 허용하되 누락을 방지합니다.
- **인덱스**: `time` 컬럼에 인덱스가 없는 경우 쿼리 부하가 클 수 있습니다.
- **오프셋 주입 전**: 기존 오프셋을 백업하고, Kafka Connect를 반드시 중지한 상태에서 주입하세요.
- **테스트 환경**: 프로덕션 적용 전 반드시 테스트 환경에서 검증하세요.
