# connector-control

## curl 예시

```sh
# 커넥터 설정파일(myconfig.json)로 PUT
curl -XPUT localhost:8083/connectors/myconnector/config -H "Content-Type: application/json" -d @myconfig.json
```

## 업데이트(PUT)

```sh
# REST api  # PUT으로 업데이트 뿐 아니라 초기 등록도 가능
PUT    /connectors/(string: connector_name)/config

# JSON format
# POST 할 때와 형식이 다름에 주의
  # "config"로 설정값을 wrap하지 않는다.
  # name은 없어도 됨. REST 주소의 커넥터 이름대로 등록됨
  # name 기술시, REST 주소의 커넥터 이름과 다르면 등록 실패
  # name 기술시, 다른 설정값과 같은 level에서 기술된다.
{
    "name": "connector_name",
    "connector.class": "io.confluent.connect.hdfs.HdfsSinkConnector",
    "tasks.max": "10",
    "topics": "test-topic",
    "hdfs.url": "hdfs://fakehost:9000",
    "hadoop.conf.dir": "/opt/hadoop/conf",
    "hadoop.home": "/opt/hadoop",
    "flush.size": "100",
    "rotate.interval.ms": "1000"
}
```

## 생성(POST), 삭제(DELETE)

```sh
# REST api
DELETE /connectors/(string: connector_name)
POST   /connectors

# JSON format
{
    "name": "connector_name",
    "config": {
        "connector.class": "io.confluent.connect.hdfs.HdfsSinkConnector",
        "tasks.max": "10",
        "topics": "test-topic",
        "hdfs.url": "hdfs://fakehost:9000",
        "hadoop.conf.dir": "/opt/hadoop/conf",
        "hadoop.home": "/opt/hadoop",
        "flush.size": "100",
        "rotate.interval.ms": "1000"
    }
}
```

### 삭제(DELETE)

```sh
# REST api
DELETE /connectors/(string: connector_name)
```

## 이슈: connect REST api 중 일부만 안되는 경우

- `/connectors`,`/connectors/plugin` 등은 되는데, connectors/(string: connector_name)는 timeout 나버리는 경우가 있음
- 커넥트 스토리지 토픽과 __consumer__offset의 replication factor가 잘못설정 되어있기 때문
- replication factor는 항상 브로커 개수와 같거나 작게 해야 함
