#!/bin/bash
##############################
# 2_build_connector_offsets.sh
#
# 설명: cutoff_ids.csv를 읽어서 Kafka Connect offset 메시지 형식으로 변환합니다.
#
# 입력: $TEMP/${TARGET_TABLE}_cutoff_ids.csv
# 출력: $TEMP/${TARGET_TABLE}_connector_offsets.txt (KEY\tVALUE TSV 형식)
#
# 환경변수:
#   TEMP         - 중간 파일 경로 (기본값: /tmp)
#   TARGET_TABLE - 대상 테이블명 (기본값: sample)
#
# 출력 형식:
#   KEY   = ["connector-name",{"protocol":"1","table":"db.table"}]
#   VALUE = {"incrementing":id}
##############################

TEMP="${TEMP:-/tmp}"

TARGET_TABLE="${TARGET_TABLE:-sample}"
INPUT_CSV="$TEMP/${TARGET_TABLE}_cutoff_ids.csv"
OUTPUT_FILE="$TEMP/${TARGET_TABLE}_connector_offsets.txt"

# 출력 파일 초기화
> "$OUTPUT_FILE"

# cutoff_ids.csv를 읽어서 오프셋 생성
# 형식: connector_name,db_name,table_name,serverid,id,formatted_time,priority
while IFS=',' read -r connector_name db_name table_name serverid final_id time priority || [ -n "$connector_name" ]; do
    # 헤더, 주석, 빈 줄 건너뛰기
    [[ "$connector_name" == "connector_name" || "$connector_name" =~ ^# || -z "$connector_name" ]] && continue

    # 전체 테이블명: db_name.table_name
    FULL_TABLE_NAME="$db_name.$table_name"

    # Key/Value 생성
    KEY="[\"$connector_name\",{\"protocol\":\"1\",\"table\":\"$FULL_TABLE_NAME\"}]"
    VALUE="{\"incrementing\":$final_id}"

    echo -e "$KEY\t$VALUE" >> "$OUTPUT_FILE"
done < "$INPUT_CSV"

echo "Offsets generated: $OUTPUT_FILE"
