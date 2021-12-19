import pytest
import model
import repository
import services


# match의 Inmemory Collection인 FakeRepository
class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


# DB의 Session을 가짜로 제공한 Fake Session
class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


# Serveice Layer에서 FakeRepository를 사용한 UnitTest
def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])  # FakeRepository는 테스트에 사용할 Batch 객체를 저장한다.

    # DB Session을 가짜로 제공한 FakeSession이 필요하다.
    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


# Serveice Layer에서 FakeRepository를 사용한 UnitTest
def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


# E2E 계층으로 부터 세 번째 테스트를 Mitgration
def test_commits():
    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True
