# Fake Object 객체

# reader, filesystem 이라는 두 가지 의존성을 노출
def sync(reader, filesystem, source_root, dest_root):
    # step 1: 입력 수집
    source_hashes = reader(source_root)  # reader로 File이 있는 Dictionary 생성
    dest_hashes = reader(dest_root)

    # step 2: 함수형 core 호출
    for sha, filename in source_hashes.items():  # 원본 폴더의 Hashes값과 filename 분리
        if sha not in dest_hashes:  # 원본 폴더의 Hashes 값이 사본 폴더에도 존재하는지 확인
            sourcepath = source_root / filename
            destpath = dest_root / filename
            filesystem.copy(destpath, sourcepath)  # filesystem을 호출해 변경 사항 적용

        elif dest_hashes[sha] != filename:  # 사본 폴더의 Hash값과 일치하는 Filename이 원본 폴더의 filename과 같은지 확인
            olddestpath = dest_root / dest_hashes[sha]
            newdestpath = dest_root / filename
            filesystem.move(olddestpath, newdestpath)

    for sha, filename in dest_hashes.items():  # 사본 폴더의 Hashes값과 filename 분리
        if sha not in source_hashes:
            filesystem.delete(dest_root / filesystem)


class FakeFileSystem(list):
    def copy(self, src, dest):
        self.append(('COPY', src, dest))

    def move(self, src, dest):
        self.append(('MOVE', src, dest))

    def delete(self, src, dest):
        self.append(('DELETE', src, dest))
