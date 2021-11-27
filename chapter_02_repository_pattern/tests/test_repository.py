import model
import repository


# SQLAlchemy의 session으로 DB Insert, Select가 정상 동작하는지 테스트
def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    # ORM 테스트 
    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    # Raw Query 테스트
    rows = session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]
