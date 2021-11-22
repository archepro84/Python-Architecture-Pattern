import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from orm import metadata, start_mappers

# test_orderline_mapper_can_load_lines, test_orderline_mapper_can_save_lines
#  함수에서 parameter에 fixture로 정의된 session을 호출하여, pytest를 실행할 때 자동으로 할당된다.
@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
