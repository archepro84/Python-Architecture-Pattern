import pytest
from adapters import repository
from domain import model
from service_layer import services


# Ficture에 사용할 Factory 함수
#  도우미 함수나 ficture로 도메인 모델을 내보내는 추상화를 한다.
class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


# 테스트가 함수를 호출하면서 원시 타입 사용
def test_returns_allocation():
    # 직접 Batch 객체를 인스턴스화 하므로 여전히 도메인에 의존하고 있다.
    batch = model.Batch("batch1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "batch1"
