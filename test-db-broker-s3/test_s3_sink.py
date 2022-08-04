
import os
import json
import pytest

# from dbextr import s3
from datetime import datetime

"""Unit Test용 모듈 (pytest 패키지 사용).

    - 테스트파일: 파일명에 test_ 또는 _test로 prefix,postfix가 붙은 파이썬 모듈을 테스트파일로 인식한다.
    - 테스트함수: unittest 패키지와 마찬가지로, 함수 앞에 test_가 붙으면 테스트용 함수로 인식한다.
    - $ pytest
        =>'모든 하위 디렉토리'의 '테스트 파일'에서 '테스트 함수'를 검사한다.
    - $ pytest {파일명.py}
        => 한 파일 내의 테스트 함수들을 검사한다. 이 땐, 파일명은 테스트파일 형식이 아니어도 된다.

    => 옵션 "-s": stdout 프린트 내용 콘솔 출력
    => 옵션 "-v": 좀 더 자세한 결과 출력

    @pytest.fixture(scope='fucntion'): 디폴트. 각 테스트함수에서 fixture함수를 콜할 때마다 실행됨
    @pytest.fixture(scope='module'): 여러 번 호출해도, 모듈(*.py) 당 최초 1번만 실행됨.
    @pytest.fixture(scope='session'): 여러 번 호출해도, 프로그램 실행동안 최초 1번만 실행됨.
"""


def _make_source_db():
    #terraform  # db ip 저장
    return

def _make_broker():
    #terraform  # broker ip 저장
    return

def _make_connect_distributed():
    #terraform # broker ip 필요
    return

def _make_connector_source_jdbc():
    #broker로 rest_api  # body에 db ip 등록 필요
    return

def _make_connector_sink_s3():
    #broker로_rest_api  #
    return