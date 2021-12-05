import hashlib
import os
import pathlib
import shutil
from pathlib import Path, PosixPath
from typing import Dict

BLOCKSIZE = 65536


def sync(source: str, dest: str):
    # step 1: 입력 수집
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)
    # step 2: 함수형 core 호출
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    # step 3: 출력 적용
    for action, *paths in actions:
        if action == "COPY":
            shutil.copyfile(*paths)
        if action == "MOVE":
            shutil.move(*paths)
        if action == "DELETE":
            os.remove(paths[0])


# 파일 경로를 입력받아 파일 해시값을 반환한다.
def hash_file(path: PosixPath):
    hasher = hashlib.sha1()  # sha1로 해시Lib 호출
    with path.open("rb") as f:
        buf = f.read(BLOCKSIZE)  # Block Size에 해당하는 만큼 file의 정보를 읽어온다.
        while buf:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
        return hasher.hexdigest()


# Application I/O 부분을 격리하는 함수
# 원본 폴더의 자식들을 순회하면서 File Name과 Hash의 Dictionary를 생성한다.
def read_paths_and_hashes(root: str):
    hashes: Dict[str, str] = {}
    for folder, _, files in os.walk(root):
        for fn in files:  # 현재 경로 Folder에 존재하는 모든 Files를 반복한다.
            hashes[hash_file(Path(folder) / fn)] = fn  # <class 'pathlib.PosixPath'>
    return hashes


# 비즈니스 로직을 determine_actions 함수로 분리
def determine_actions(source_hashes: Dict[str, str], dest_hashes: Dict[str, str],
                      source_folder: str, dest_folder: str):
    for sha, filename in source_hashes.items():  # 원본 폴더의 Hashes값과 filename 분리
        if sha not in dest_hashes:  # 원본 폴더의 Hashes 값이 사본 폴더에도 존재하는지 확인
            sourcepath = Path(source_folder) / filename
            destpath = Path(dest_folder) / filename
            yield "COPY", sourcepath, destpath

        elif dest_hashes[sha] != filename:  # 사본 폴더의 Hash값과 일치하는 Filename이 원본 폴더의 filename과 같은지 확인
            olddestpath = Path(dest_folder) / dest_hashes[sha]
            newdestpath = Path(dest_folder) / filename
            yield "MOVE", olddestpath, newdestpath

    for sha, filename in dest_hashes.items():  # 사본 폴더의 Hashes값과 filename 분리
        if sha not in source_hashes:
            yield "DELETE", dest_folder / filename


if __name__ == '__main__':
    import tempfile

    source = tempfile.mkdtemp()  # 임시 디렉터리 생성
    dest = tempfile.mkdtemp()  # 임시 디렉터리 생성

    content = "I am a file that was renamed"

    source_path = Path(source) / "source-filename"  # <class 'pathlib.PosixPath'>
    old_dest_path = Path(dest) / "dest-filename"  # <class 'pathlib.PosixPath'>
    expected_dest_path = Path(dest) / "source-filename"  # <class 'pathlib.PosixPath'>

    source_path.write_text(content)
    old_dest_path.write_text(content)
    sync(source, dest)
