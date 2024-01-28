# kafka replication factor

```sh
- broker 수와 같거나 작은 값으로 설정
- broker 수보다 1개 작게 해놓으면 좋음(broker 하나가 죽어도 지속적 동작, 업데이트시 편함) 
- Scale-in 시 2 이상
```

```server.properties
# server.properties에서 신규 생성 토픽의 default replication factor 설정 예
default.replication.factor=3

# 오프셋 토픽의 초기 replication factor 설정 예
offsets.topic.replication.factor=1
```

## 기타

### min.insync.replicas

- 보통 브로커 3개라면 2 정도 권장
- 브로커 1개라면 1
- [참고](https://songhayoung.github.io/2020/07/13/kafka/acks-replicas/#Introduction)
