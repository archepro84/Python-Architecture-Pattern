import hashlib
import os
import pathlib
from pathlib import PosixPath
import shutil
from pathlib import Path
from typing import List, Dict, Optional

BLOCKSIZE = 65536


def sync(source, dest):
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


# File을 Hash하기
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
def read_paths_and_hashes(root):
    hashes: Dict = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            # print(f"Folder : {folder}")
            # print(f"fn : {fn}")
            # print(f"Path(folder) / fn : {Path(folder) / fn}", end="\n\n")
            hashes[hash_file(Path(folder) / fn)] = fn  # <class 'pathlib.PosixPath'>
    return hashes


# 비즈니스 로직을 determine_actions 함수로 분리
def determine_actions(source_hashes, dest_hashes, source_folder, dest_folder):
    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            sourcepath = Path(source_folder) / filename
            destpath = Path(dest_folder) / filename
            yield "COPY", sourcepath, destpath

        elif dest_hashes[sha] != filename:
            olddestpath = Path(dest_folder) / dest_hashes[sha]
            newdestpath = Path(dest_folder) / filename
            yield "MOVE", olddestpath, newdestpath

    for sha, filename in dest_hashes.items():
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

    print(old_dest_path.exists() is False)  # dest.File이 사본이므로 삭제된 것을 테스트
    print(Path(dest).exists())
    print(expected_dest_path.read_text() == content)  # 처음입력한 content와 File.write Text가 같은지 테스트
    print(dest)
