import os
import util
from datetime import datetime
from connectors import jdbc_src_super

#####################################
# 커넥터 생성
#####################################
# connectors 경로에서 jdbc_src가 포함된 파일목록 가져오기
WORK_DIR = os.getcwd()
connectors = util.get_connectors(f'{WORK_DIR}/connectors_codetable/jdbc_src_*.json')  # NOQA

# 공통사항 반영
common = jdbc_src_super.super
for connector in connectors:
    config = connector['config']
    config.update(common['config'])
    connector['config'] = config

# 차이 반영 (원칙적으로 각 커넥터 파일에 있을 내용이지만, 편의상 사용)
for connector in connectors:
    table = str(connector['name']).replace('jdbc_src_', '')
    topic = str(connector['config']['topic.prefix'])
    query = str(connector['config']['query'])
    diff = {
        "topic.prefix": topic.format(table=table),
        "query": topic.format(table=table),
    }
    config = connector['config']
    config.update(diff)
    connector['config'] = config

# 토픽 및 커넥터 생성
now = datetime.today().strftime("%y%m%d_%H%M")
for connector in connectors:
    connector['name'] = connector['name'] + '_' + now
    util.create_topic(topic=str(connector['config']['topic.prefix']), partitions=1)  # NOQA
    util.create_connector(connector)


util.show_connectors()
util.show_topics()
