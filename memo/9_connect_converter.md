# 카프카 커넥트 사용시, converter 종류

- BytesArray: 완전 동일하게 데이터를 옮길 때 씀
- Avro: Schema Registry 사용시 많이 씀
- Json: Kafka에서 Json형식으로 데이터를 관리하는 경우가 많으므로, 가장 일반적

## 일반적인 경우 default

```properties
key.converter: Json
value.converter: Json
```

- Kafka에서 가장 널리 사용되는 저장형식
- 개별 connector에서 별도 설정하지 않으면 connect 설정파일(`connect-standalone.properties`, `connect-distributed`.properties)을 따른다.

## MirrorMaker2

```properties
key.converter: BytesArray
value.converter: BytesArray
```

- 그대로 복제(미러링)하는 것이 목적이므로 기본 설정이 BytesArray다.
  - BytesArray가 아니면, 문자인코딩, 스키마 포함여부 등 신경쓸 것이 많아진다.
- 다만 위와 같이 알려져있으나, 기존 dstributed connect에 MM2 connector를 붙일 경우, connect설정을 기본으로 따르게 된다.
- MirrorMaker2를 쓸 경우 BytesArray로 반드시 명시를 해주자.
