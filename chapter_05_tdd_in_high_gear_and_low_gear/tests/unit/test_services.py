import pytest
from adapters import repository
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


# Service layer의 공식적인 유스 케이스만 사용하는 서비스 계층 테스트
#  도메인에 대한 의존 관계를 모두 제거할 수도 있다.
def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


# 테스트가 함수를 호출하면서 원시 타입 사용
def test_returns_allocation():
    # 직접 Batch 객체를 인스턴스화 하므로 여전히 도메인에 의존하고 있다.
    batch = model.Batch("batch1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "batch1"


# 도메인 모델에 의존성을 제거한 Service layer 테스트
def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "batch1"


# 도메인 모델에 의존성을 제거한 Service layer 테스트
def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())
