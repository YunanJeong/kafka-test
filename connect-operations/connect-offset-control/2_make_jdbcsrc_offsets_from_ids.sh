#!/bin/bash
##############################
# 2_make_kv_offsets_from_id_list.sh
#
# 설명: id_list.csv 파일을 읽어서 Kafka Connect offset 형식으로 변환하여
#       offsets_to_inject.txt 파일을 생성합니다.
#
# 입력: tmp/id_list.csv (connector_name,db_name,table_name,serverid,id,formatted_time,priority)
# 출력: tmp/offsets_to_inject.txt (KEY\tVALUE 형식)
#
# 출력 형식:
#   KEY   = ["connector-name",{"protocol":"1","table":"db.table"}]
#   VALUE = {"incrementing":id}
##############################

TEMP='./tmp'

INPUT_CSV="$TEMP/${TABLE}_id_list.csv"
OUTPUT_FILE="$TEMP/${TABLE}_offsets_to_inject.txt"

# 출력 파일 초기화
> "$OUTPUT_FILE"

# id_list.csv를 읽어서 오프셋 생성
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
