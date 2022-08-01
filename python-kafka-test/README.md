# python-kafka-test
- python kafka test

## Kafka python package
- `confluent-kafka-python`: confluent 공식, C extension 활용, 처리속도 빠름, Windows에서 사용하기 힘든 이슈있다고 함, C extension으로 인해 디버그 힘듦, 비동기처리시 시간순 제어 가능.
- `kafka-python`: pure python, 쓰기 편함, confluent-kafka-python에 비해 느림, 속도 개선이 필요한 경우 변경 필요. 비동기처리시 시간순 제어 불가.
- `pykafka`: 2018년 이후 유지보수 미비
- 참고
	- https://towardsdatascience.com/3-libraries-you-should-know-to-master-apache-kafka-in-python-c95fdf8700f2
	- https://zhuanlan.zhihu.com/p/156812909
