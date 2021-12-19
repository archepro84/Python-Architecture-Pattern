import uuid
import pytest
import requests

import config


# 난수 문자열을 생성하는 도우미 함수
def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


@pytest.mark.usefixtures("restart_api")
def test_api_returns_allocation(add_stock):
    # 실제 DB를 사용하므로 테스트와 프로그램 실행이 서로 영향을 미치지 못하게 분리한다.
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)

    # SQL로 DB Insert를 도와주는 도우미 Fixture
    add_stock(
        [
            (laterbatch, sku, 100, "2011-01-02"),
            (earlybatch, sku, 100, "2011-01-01"),
            (otherbatch, othersku, 100, None),
        ]
    )
    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()  # config.py는 설정 정보를 저장

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


# DB 상태를 나중에 검사하는지, 이미 할당해서 Batch를 모두 소진한경우 두 번째 라인이 할당 되지 않아야 한다는 것을 검증
# DB Commit이 존재하지 않는다.
@pytest.mark.usefixtures("restart_api")
def test_allocations_are_persisted(add_stock):
    sku = random_sku()
    batch1, batch2 = random_batchref(1), random_batchref(2)
    order1, order2 = random_orderid(1), random_orderid(2)
    add_stock(
        [
            (batch1, sku, 10, "2011-01-01"),  # batch1: 10개 할당
            (batch2, sku, 10, "2011-01-02"),  # batch2: 10개 할당
        ]
    )
    line1 = {"orderid": order1, "sku": sku, "qty": 10}  # line1: 10개 소진
    line2 = {"orderid": order2, "sku": sku, "qty": 10}  # line2: 10개 소진
    url = config.get_api_url()

    # 첫 번째 주문은 Batch 1에 있는 모든 재고를 소진한다.
    r = requests.post(f"{url}/allocate", json=line1)
    assert r.status_code == 201
    assert r.json()["batchref"] == batch1

    # 두 번째 주문은 Batch 2로 가야 한다.
    r = requests.post(f"{url}/allocate", json=line2)
    assert r.status_code == 201
    assert r.json()["batchref"] == batch2


# 재고보다 더 많은 단위를 할당하려고 시도한다.
@pytest.mark.usefixtures("restart_api")
def test_400_message_for_out_of_stock(add_stock):
    sku, small_batch, large_order = random_sku(), random_batchref(), random_orderid()

    add_stock(
        [
            (small_batch, sku, 10, "2011-01-01"),  # 10개의 재고 할당
        ]
    )
    data = {"orderid": large_order, "sku": sku, "qty": 20}  # 10개 재고보다 더 많은 20개 소진
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Out of stock for sku {sku}"


# sku가 존재하지 않는다. 앱의 관점에서 이 sku는 올바른 sku가 아니다.
@pytest.mark.usefixtures("restart_api")
def test_400_message_for_invalid_sku():
    unknown_sku, orderid = random_sku(), random_orderid()

    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}  # 재고가 존재하지 않는데, 20개를 소진
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"


# 정상 경로 테스트
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)

    add_stock(
        [
            (earlybatch, sku, 100, "2011-01-01"),
            (laterbatch, sku, 100, "2011-01-02"),
            (otherbatch, othersku, 100, None),
        ]
    )
    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


# 비정상 경로 테스트
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()

    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"
