"""Bulk 모드 테스트.

- bulk모드에서 query 옵션 사용시 where절 사용가능하다.
- bulk모드에서 query 옵션과 whitelist, blacklist는 같이 사용할 수 없다.(테이블 지정 중첩되므로)

- whitelist로 다수 테이블을 bulk 추출 시 (query옵션 사용안할 때),
    - 테이블명을 나열하면 일반적인 SQL Server 쿼리처럼 해당DB명과 dbo스키마가 사용된다.
        - e.g) tablename => TutorialDB.dbo.tablename

    - 다음 옵션들을 활용할 수 있다.
        - catalog.pattern: 카탈로그 지정(DB명에 해당)
        - schema.pattern: 스키마 지정(MSSQL Server의 "dbo"가 이에 해당한다.)
        - catalog 및 schema 정보는 다음 쿼리로 확인할 수 있다.
            - SELECT * FROM {db_name}.INFORMATION_SCHEMA.tables

    - 위 옵션 대신 테이블명에 모두 기술해도 된다.
    - 여러 DB, 여러 schema를 참조하는 경우, table명에 한번에 써야한다.
        - e.g) [TutoiralDB1.dbo1.table1, TutorialDB2.dbo2.table2]
    - (★중요)테이블명만 써도 일반적으로 괜찮지만, 다양한 view를 제공하는 라이브DB에서는 오류가 발생할 수 있다.

- (★중요★)대상 DB의 정확한 구조를 알 수 없는 경우(DB관리팀에서 제한된 schema(alias, view)를 제공하는 경우)
    - catalog, schema 설정이 의도대로 작동하지 않을 수 있다.
    - query 옵션을 사용하는 것이 더 안정적이다.

    - 221021 JDBC Source Connector 소스코드 분석결과
        => 여러 schema에 같은 이름 테이블이 있는 경우, schema인식 오류 이슈 발생
        => ★ 결론: MS SQL SERVER은 query모드를 쓰거나, 커넥터 소스코드를 살짝 수정해야한다.
        => SQL SERVER가 아니라면 다음 방법을 시도해볼 수 있다.
            => whitelist 기술방식 시도 e.g) table => schema.table 또는 catalog.schema.table
            => table.types, catalog.pattern, schema.pattern 옵션 등 조합
            => connection.url에 schema 명시

- batch.max.rows: 한번에 가져오는 batch의 최대 row 수
    - batch.max.rows는 connect(connector)의 buffer 크기를 의미한다.
    
    - bulk모드는 항상 테이블내용 전체를 한번에 가져온다. 한 테이블이 중간에 잘리지 않는다.
        - jdbc connector 2022년 초중반까지 버전에서는 bulk모드일 때도 이 설정값에 따라 가져오는 rows가 잘렸다.
    - timestamp 모드에서는 batch.max.rows가 너무 작으면 값이 누락될 수 있다.
    - bulk모드의 "batch.max.rows" 옵션은 다른모드일 때와 작동방식이 약간 다르다.
        - bulk: 1회 polling시, 전체 테이블 내용을 가져오지만, batch.max.rows 크기만큼 나눠서 broker의 topic에 적재된다. (도중에 record는 connect buffer를 거침)
        - timestamp, incrementing: (1회 polling시 가져오는 분량) = (batch.max.rows 크기)
    - 특히 해당 topic을 지속적으로 consume하는 consumer, connector가 있다면, batch.max.rows 크기 단위로 중간에 스트리밍 흐름이 끊길 수 있다.
        - e.g.) topic의 record를 file 단위로 consume할 때, 원래 하나로 처리되어야할 file이 나눠질 수 있음

"""

import json
import requests

####################################
# 보안 주의. git push 주의
####################################
connect_ip = 'localhost:8083'

db_ip = 'localhost:1433'
db_name = 'TutorialDB'
db_user = 'tester'
db_pass = 'tester^381'
db_table = 'Customers'
incrementing_col = 'CustomerId'
timestamp_col = 'regdate'
incrementing_initial = "RegDate > CONVERT(DATETIME, '2022-05-11 00:00:01.000')"
####################################

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


db_tables = ['TutorialDB.dbo.Customers', 'TutorialDB.dbo.Customers2', ]
body = {
    "name": "jdbc-bulktest",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",

        "tasks.max": "11",
        "connection.url": f"jdbc:sqlserver://{db_ip};databaseName={db_name}",
        "connection.user": db_user,
        "connection.password": db_pass,
        "mode": "bulk",
        "topic.prefix": "test-bulk",

        # "query": query,
        "db.timezone": "Asia/Seoul",
        "table.whitelist": ','.join(db_tables),  # 특정 테이블들만 조회
        # "table.types": "VIEW",     # default: TABLE
        # "table.blacklist": "xxx",  # 특정 테이블 제외
        # "catalog.pattern": db_name,

        # "schema.pattern": "dbo",

        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": False,

        "poll.interval.ms": 1500000,  # default: 5000ms
        "batch.max.rows": 1000,  # default: 100개  # 벌크모드에서는 작동방식 다름
        "timestamp.delay.interval.ms": 2000,  # default: 0ms

    }
}

kafka_connect = 'http://'+connect_ip+'/connectors'
response = requests.post(kafka_connect, json.dumps(body, ensure_ascii=False), headers=headers)
print(response)