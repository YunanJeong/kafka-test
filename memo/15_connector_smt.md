# SMT(Single Message Transformations)

- 커넥터에서 간단한 메시지 변환을 할 수 있도록 해주는 기능
- kstreams, ksqldb 등을 쓰기 애매할 때 유용하게 사용가능
- 커넥터의 config에서 설정가능
- `커넥터 유형마다 사용가능한 SMT의 기능이 제한`되며, 이는 일반적으로 문서에 잘 나와있음
- SMT의 confluent 일부 문서가 부실하거나 오류가 있으니 주의

## SMT가 적용되는 시점 (중요)

- 커넥터 핵심 기능 수행 후 `출력직전 SMT 적용`
- source connector: kafka에 쓰기 직전 데이터 변환됨
- sink connector: 외부 시스템으로 전송 직전 데이터 변환됨

## 용례: SMT 중 TimestampConverter로 시간 값 변환 (String to String)

### 상황

### 원본

```json
{"myEventTime": "2024-05-24 15:00:01"}
```

- S3 Sink Connector로 Kafka Record를 S3로 업로드하려 한다.
- TimeBasedPartitioner로 업로드하려는데, 원본 시간문자열이 ISO8601 표준을 따르지 않아 제대로 인식이 안된다.

### 결과

```json
{"myEventTime": "2024-05-24T15:00:01.000+09:00"}
```

- S3 Sink Connector의 경우 SMT 적용 후 Partitioner가 적용된다. (Partitioner는 최종 출력 단계로 취급되기 때문)
- TimeBasedPartitioner는 표준 시간 문자열 필드를 참조하여 정상적으로 작동한다.

### 설정

```yaml
##################################################################
# SMT: "비표준 문자열 시간"을 "ISO8601 표준 문자열 시간"으로 변경
##################################################################
# SMT string to string 변환은 직접 지원되지 않으므로, timestamp로 중간변경을 거친다.
transforms: StrToStamp,StampToStr
transforms.StrToStamp.type: "org.apache.kafka.connect.transforms.TimestampConverter$Value"
transforms.StrToStamp.field: myLogEventTime
transforms.StrToStamp.format: "yyyy-MM-dd HH:mm:ss" # 입력 형식 (원본로그에 timezone 표기가 없어서 UTC 시간으로 인식되어 변환. 이는 시스템 및 설정 시간과 무관)
transforms.StrToStamp.target.type: Timestamp
# 중간변경된 timestamp는 그대로 사용할 수 없다.
# 원본시간은 KST시간이지만 타임존 표기가 없어서, UTC취급되어 timestamp로 변환되었기 때문이다. (실제 필요값과 9시간 차이 발생) 
# 따라서, 다시 string(ISO8601)으로 변경할 때, 타임존을 패턴(XXXXX)이 아니라 상수('+09:00')로 입력해준다.
# SMT로 값이 변경된 후 TimeBasedPartitioner는 시간값을 올바르게 인식한다.
transforms.StampToStr.type: "org.apache.kafka.connect.transforms.TimestampConverter$Value"
transforms.StampToStr.field: myLogEventTime
transforms.StampToStr.format: "yyyy-MM-dd'T'HH:mm:ss.SSS'+09:00'"  # 출력 형식: ISO8601로 표기(시간대를 직접기입)  
transforms.StampToStr.target.type: string

```
