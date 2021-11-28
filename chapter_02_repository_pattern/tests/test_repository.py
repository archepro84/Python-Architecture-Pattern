import model
import repository


# SQLAlchemy의 session으로 DB Insert, Select가 정상 동작하는지 테스트
def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    # ORM 테스트
    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)  # DB Insert
    session.commit()  # Commit

    # Raw Query 테스트
    rows = list(session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
    ))
    assert rows == [("batch1", "RUSTY-SOAPDISH", 100, None)]


# order_lines Table Insert 테스트
def insert_order_line(session):
    # DB Insert Raw Query
    session.execute(
        "INSERT INTO order_lines (orderid, sku, qty)"
        ' VALUES ("order1", "GENERIC-SOFA", 12)'
    )
    # DB Select Raw Query
    [[orderline_id]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id


# batches Table Insert 테스트
def insert_batch(session, batch_id):
    # DB Insert Raw Query
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)',
        dict(batch_id=batch_id),
    )
    # DB Select Raw Query
    [[batch_id]] = session.execute(
        'SELECT id FROM batches WHERE reference=:batch_id AND sku="GENERIC-SOFA"',
        dict(batch_id=batch_id),
    )
    return batch_id


# allocations Table Insert 테스트
def insert_allocation(session, orderline_id, batch_id):
    # DB Insert Raw Query
    session.execute(
        "INSERT INTO allocations (orderline_id, batch_id)"
        " VALUES (:orderline_id, :batch_id)",
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


# reposity Pattern을 이용한 DB 테스트
def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = insert_order_line(session)  # order_line Table Insert
    batch1_id = insert_batch(session, "batch1")  # batches Table Insert
    insert_batch(session, "batch2")  # batches Table Insert
    insert_allocation(session, orderline_id, batch1_id)  # allocations Table Insert

    repo = repository.SqlAlchemyRepository(session)  # session을 삽입하여 Repository Class 할당
    retrieved = repo.get("batch1")  # Repository의 최초 1행 반환

    # insert_batch로 할당한 것과 model.Batch로 할당한 Batch 데이터 비교
    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ 는 단순히 참조를 비교 / Magic Method __eq__ 사용
    assert retrieved.sku == expected.sku  # GENERIC-SOFA를 삽입한 내용과 Batch에서 조회한 데이터 비교
    assert retrieved._purchased_quantity == expected._purchased_quantity  # 3번째 인자 비교
    assert retrieved._allocations == {
        model.OrderLine("order1", "GENERIC-SOFA", 12),  # _allocations는 OrderLine 객체의 파이썬 집합 비교
    }
