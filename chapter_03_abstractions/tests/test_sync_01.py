# doc : https://docs.python.org/ko/3/library/tempfile.html
import tempfile  # 임시 파일과 임시 디렉터리를 생성하는 Lib
# doc : https://docs.python.org/ko/3/library/shutil.html
import shutil  # 고수준 파일 연산용 Lib
# doc : https://docs.python.org/ko/3/library/pathlib.html
from pathlib import Path  # 객체 지향 파일 시스템 경로 Lib
from sync_01 import sync


# # sync_01 테스트 코드

# 엔드 투 엔드 테스트
def test_when_a_file_exists_in_the_source_but_not_the_destination():
    try:
        source = tempfile.mkdtemp()  # 임시 디렉터리 생성
        dest = tempfile.mkdtemp()  # 임시 디렉터리 생성

        content = "I am a very useful file"
        (Path(source) / "my-file").write_text(content)

        sync(source, dest)

        expected_path = Path(dest) / "my-file"
        assert expected_path.exists()
        assert expected_path.read_text() == content

    finally:
        shutil.rmtree(source)
        shutil.rmtree(dest)


# 도메인 로직이 I/O 코드와 긴밀히 결합되어 있다.
# 고수준 코드는 저수준 세부 사항과 결합되어 있어, 다뤄야 할 시나리오가 복잡해져 테스트 작성이 어려워진다.
def test_when_a_file_has_been_renamed_in_the_source():
    try:
        source = tempfile.mkdtemp()  # 임시 디렉터리 생성
        dest = tempfile.mkdtemp()  # 임시 디렉터리 생성

        content = "I am a file that was renamed"
        source_path = Path(source) / "source-filename"
        old_dest_path = Path(dest) / "dest-filename"
        expected_dest_path = Path(dest) / "source-filename"
        source_path.write_text(content)
        old_dest_path.write_text(content)

        sync(source, dest)

        assert old_dest_path.exists() is False  # 사본파일이 삭제된 것을 테스트
        assert expected_dest_path.read_text() == content  # 처음입력한 content와 File.write Text가 같은지 테스트

    finally:
        shutil.rmtree(source)
        shutil.rmtree(dest)


# 테스트를 위한 단순화한 입력과 출력
def test_when_a_file_exists_in_the_source_but_not_the_destination():
    src_hashes = {'hash1': 'fn1'}
    dst_hashes = {}
    expected_actions = [('COPY', '/src/fn1', '/dst/fn1')]


# 테스트를 위한 단순화한 입력과 출력
def test_when_a_file_has_been_renamed_in_the_source():
    src_hashes = {'hash1': 'fn1'}
    dst_hashes = {'hash1': 'fn2'}
    expected_actions = [('MOVE', '/dst/fn2', '/dst/fn1')]
