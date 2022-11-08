"""util.py."""

import os
import json
import yaml
import requests
import glob
from time import sleep
from datetime import datetime
from pathlib import Path

KAFKA_HOME = '/usr/local/kafka'
KCONNECT_HOME = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()  # NOQA

CONNECT_DEFAULT = 'localhost:8083'
BROKER_DEFAULT = 'localhost:9092'


def send_http(url, body):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    res = requests.post(url, json.dumps(body, ensure_ascii=False), headers=headers)  # NOQA
    return res


def get_yaml(filepath):
    with open(filepath, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


def get_json(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


def get_connectors(path):
    """Connector 설정 파일을 리스트로 반환."""
    connectors = []
    paths = glob.glob(path)
    for filepath in paths:
        data = get_json(filepath)
        connectors += [data]
    return connectors


def create_connector(connector, suffix=False, connect=CONNECT_DEFAULT):
    """커넥터 생성. 커넥트가 Distributed 모드일 때 사용.

    Args:
        - connector (dict): 커넥터 json. http body.
        - suffix (bool):    커넥터 이름에 날짜표기 유무 (default: False)
        - connect (str):    {IP}:{Port}
    """
    if suffix is True:
        now = datetime.today().strftime("%y%m%d")
        connector['name'] = connector['name'] + '_' + now
    sleep(1)
    res = send_http(f'http://{connect}/connectors', connector)
    print(res)


def delete_connector(connector_name, connect=CONNECT_DEFAULT):
    cmd = f'curl {connect}/connectors/{connector_name} -XDELETE'
    os.system(cmd)


def show_connectors(connect=CONNECT_DEFAULT):
    cmd = f'curl {connect}/connectors | jq | sort'
    os.system(cmd)


def show_connector(connector, connect=CONNECT_DEFAULT):
    cmd = f'curl {connect}/connectors/{connector} | jq | sort'
    os.system(cmd)


#########################################################################


def create_topic(topic, partitions, replications=1,
                 broker=BROKER_DEFAULT):
    """커넥터 생성. 커넥트가 Distributed 모드일 때 사용.

    Args:
        - topic (str):         토픽명
        - partitions (int):    파티션 수
        - replications (int):  리플리케이션팩터 수
        - broker (str):        {IP}:{Port}, (default:localhost:9092)

    Note:
        - 토픽 생성. 이미 토픽이 존재하면 에러만 출력 후 변화없음.
    """
    cmd = f'{KAFKA_HOME}/bin/kafka-topics.sh' \
        + f' --create --topic {topic}' \
        + f' --bootstrap-server {broker}' \
        + f' --partitions {partitions} --replication-factor {replications}'
    os.system(cmd)


def delete_topic(topic, broker=BROKER_DEFAULT):
    """토픽 삭제. 사용 주의."""
    # server.properties에 delete.topic.enable=true 필요 (default)
    cmd = f'{KAFKA_HOME}/bin/kafka-topics.sh' \
        + f' --bootstrap-server {broker}' \
        + f' --topic {topic} --delete'
    os.system(cmd)


def show_topics(broker=BROKER_DEFAULT):
    cmd = f'kafkacat -b {broker} -L | grep topic'
    os.system(cmd)


def show_records(topic, broker=BROKER_DEFAULT):
    cmd = f'kafkacat -b {broker} -t {topic} -q -e'
    os.system(cmd)


def test_fucntion():
    print('test')