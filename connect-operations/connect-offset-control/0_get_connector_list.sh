#!/bin/bash
##############################
# 0_get_connector_list.sh
#
# 설명: Kafka Connect API에서 JDBC Source Connector 정보를 조회하여
#       con_list.json 파일을 생성합니다.
#
# 입력: Kafka Connect REST API (http://localhost:8083/connectors)
# 출력: tmp/con_list.json (JSON Lines 형식)
#
# 환경변수:
#   DB_USER  - DB 사용자명 (기본값: default_user)
#   DB_PASS  - DB 비밀번호 (기본값: default_password)
##############################

# 모든 JDBC Source 커넥터의 DB연결정보 추출하기

curl -s "http://localhost:8083/connectors?expand=info" | jq -c -r '
  to_entries[] | 
  select(.value.info.config["connector.class"] == "io.confluent.connect.jdbc.JdbcSourceConnector") | 
  {
    name: .key,
    url: .value.info.config["connection.url"],
    catalog: .value.info.config["catalog.pattern"],
    user: .value.info.config["connection.user"],
    password: .value.info.config["connection.password"]
  }
'

# 컨테이너 내부에 파일 저장 (컨테이너 안에서 실행)
# curl -s "localhost:8083/connectors?expand=config" | jq '...' > /tmp/result.json
# 호스트로 복사 (호스트 터미널에서 실행)
# docker cp <container_id_or_name>:/tmp/result.json ./result.json

###############################
# 쿠버네티스 노드 호스트에서 실행
###############################
# kubectl exec <pod_name> -n <namespace> -- bash -c \
# "curl -s localhost:8083/connectors?expand=info | jq -r 'to_entries[] | select(.value.info.config[\"connector.class\"] == \"io.confluent.connect.jdbc.JdbcSourceConnector\") | {name: .key, url: .value.info.config[\"connection.url\"], catalog: .value.info.config[\"catalog.pattern\"], user: .value.info.config[\"connection.user\"], password: .value.info.config[\"connection.password\"]}'" \
# > jdbc_source_configs.json
