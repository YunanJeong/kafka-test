#!/bin/bash
##############################
# 1_get_timebase_id_from_dbs.sh
#
# 설명: con_list.json 파일의 각 DB에 접속하여 특정 시간 기준으로
#       ID를 조회하고 결과를 id_list.csv에 저장합니다.
#
# 입력: tmp/con_list.json (커넥터 정보 JSON)
# 출력: tmp/id_list.csv (connector_name,db_name,table_name,serverid,id,formatted_time,priority)
#
# 환경변수:
#   TABLE       - 조회할 테이블명 (기본값: default_tablename)
#   TARGET_TIME - 타겟 시간 Unix timestamp (기본값: 1767193200)
#
# 동작 원리:
#   1. 타겟 시간 이후 첫 번째 행을 찾아 ID-1 반환 (누락 방지)
#   2. 데이터가 없으면 전체 최대 ID 행 반환
##############################

TEMP='./tmp'

# --- 설정 구간 ---
TARGET_TIME=1767193200   # 2026/01/01
TABLE="${TABLE:-default_tablename}"


INPUT_FILE="$TEMP/con_list.json" # JSON 형식
OUTPUT_FILE="$TEMP/id_list.csv"


# 헤더 생성
echo "connector_name,db_name,table_name,serverid,id,formatted_time,priority" > "$OUTPUT_FILE"

# JSON 파일을 한 줄씩 읽어서 처리
while IFS= read -r line || [ -n "$line" ]; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue

    # JSON에서 필드 추출
    connector_name=$(echo "$line" | jq -r '.name')
    url=$(echo "$line" | jq -r '.url')
    user=$(echo "$line" | jq -r '.user')
    pw=$(echo "$line" | jq -r '.password')
    db=$(echo "$line" | jq -r '.catalog')

    # URL에서 호스트, 포트 파싱
    # jdbc:mysql://host:port/database?params 형태
    temp=${url#jdbc:mysql://}
    temp=${temp%\?*}
    host_port=${temp%/*}

    if [[ "$host_port" == *":"* ]]; then
        host=${host_port%:*}
        port=${host_port#*:}
    else
        host=$host_port
        port=3306
    fi

    echo "Querying: $connector_name ($host:$port / $db)..."

    # SQL 쿼리 본체. time 기준으로 가장 가까운 id를 찾는 로직
    # 특정시간 이후 가장 가까운 id 검색 후 1뺀다
    # null일시 테이블 내 가장 큰 id 반환.(특정시간보다 미래의 데이터가 없으므로 전체(과거)데이터 중 최신을 고르는 것)
    # 커넥터명과 매치를 위해 최종결과물에 커넥터,DB,Table 이름 넣기
    # id만 인덱스, time은 인덱스 없으므로 쿼리 부하에 주의하여 작성
    # 최종적으로 null일시, 해당 table에 데이터가 없는 것임
    QUERY="
SELECT
    '$connector_name' AS connector_name,
    '$db' AS db_name,
    '$TABLE' AS table_name,
    res.serverid,
    IF(res.p = 1, res.id - 1, res.id) AS final_id,
    FROM_UNIXTIME(res.time),
    res.p
FROM (
    (
      -- 1순위: 타겟 시간 직후 행 (최신 데이터부터 역순 스캔 유도)
      SELECT serverid, id, time, 1 AS p
      FROM $TABLE
      WHERE time >= $TARGET_TIME
      ORDER BY time ASC, id ASC
      LIMIT 1
    )
    UNION ALL
    (
      -- 2순위: 1순위 부재 시 전체 최대 ID 행
      SELECT serverid, id, time, 2 AS p
      FROM $TABLE
      ORDER BY id DESC
      LIMIT 1
    )
) AS res
ORDER BY res.p ASC
LIMIT 1;"


    # TEST 출력
    echo " mysql -h\"$host\" -P\"$port\" -u\"$user\" -p\"$pw\" -D\"$db\" -N -s -e \"$QUERY\" 2>/dev/null | sed 's/\t/,/g' >> \"$OUTPUT_FILE\" "

    # mysql 실행 (-P 옵션에 파싱된 port 적용)
    # mysql -h"$host" -P"$port" -u"$user" -p"$pw" -D"$db" -N -s -e "$QUERY" 2>/dev/null | sed 's/\t/,/g' >> "$OUTPUT_FILE"

    # if [ ${PIPESTATUS[0]} -eq 0 ]; then
    #     echo "Done: $connector_name ($host)"
    # else
    #     echo "Fail: $connector_name ($host)" >&2
    # fi

done < "$INPUT_FILE"

echo "Completed. Check $OUTPUT_FILE"