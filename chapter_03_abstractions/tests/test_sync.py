# doc : https://docs.python.org/ko/3/library/tempfile.html
import tempfile  # 임시 파일과 임시 디렉터리를 생성하는 Lib
# doc : https://docs.python.org/ko/3/library/shutil.html
import shutil  # 고수준 파일 연산용 Lib
# doc : https://docs.python.org/ko/3/library/pathlib.html
from pathlib import Path  # 객체 지향 파일 시스템 경로 Lib
from sync import sync, determine_actions


# 엔드 투 엔드 테스트
def test_when_a_file_exists_in_the_source_but_not_the_destination():
    source_hashes = {"hash1": "fn1"}
    dest_hashes = {}

    # 저수준 I/O 세부 사항 사이의 얽힘을 풀었기 때문에 쉽게 비즈니스 로직을 테스트할 수 있다.
    actions = determine_actions(source_hashes, dest_hashes, Path("/src"), Path("/dst"))
    assert list(actions) == [("COPY", Path("/src/fn1"), Path("/dst/fn1"))]


# 도메인 로직이 I/O 코드와 긴밀히 결합되어 있다.
# 고수준 코드는 저수준 세부 사항과 결합되어 있어, 다뤄야 할 시나리오가 복잡해져 테스트 작성이 어려워진다.
def test_when_a_file_has_been_renamed_in_the_source():
    source_hashes = {"hash1": "fn1"}
    dest_hashes = {"hash1": "fn2"}

    # 저수준 I/O 세부 사항 사이의 얽힘을 풀었기 때문에 쉽게 비즈니스 로직을 테스트할 수 있다.
    actions = determine_actions(source_hashes, dest_hashes, Path("/src"), Path("/dst"))
    assert list(actions) == [("MOVE", Path("/dst/fn2"), Path("/dst/fn1"))]
