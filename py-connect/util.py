"""221021
"""

import os
import json
import requests
import glob
from time import sleep

CONNECT_DEFAULT = 'localhost:8083'
KAFKA_HOME = '/usr/local/kafka'
BROKER_DEFAULT = 'localhost:9092'
WORK_DIR = os.getcwd()


def send_http(url, body):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    res = requests.post(url, json.dumps(body, ensure_ascii=False), headers=headers)  # NOQA
    return res


def get_connectors(filepath):
    """Connector 설정 파일을 리스트로 반환."""
    connectors = []
    path_list = glob.glob(filepath)
    for path in path_list:
        with open(path, 'r') as file:
            data = json.load(file)
        connectors += [data]
    return connectors


def create_connector(connector, connect=CONNECT_DEFAULT):
    """커넥터 생성. 커넥트가 Distributed 모드일 때 사용.

    Args:
        connector (dict): 커넥터 json. http body.
        connect (str):    {IP}:{Port}
    """
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
    cmd = f'curl {connect}/{connector} | jq | sort'
    os.system(cmd)

#########################################################################


def create_topic(topic, partitions, replications=1,
                 broker=BROKER_DEFAULT):
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
