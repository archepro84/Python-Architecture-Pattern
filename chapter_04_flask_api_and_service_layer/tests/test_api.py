import uuid
import pytest
import requests

import config


@pytest.mark.usefixtures('restart_api')
def test_api_returns_allocation(add_sotck):
    # 난수 문자열을 생성하는 도무이 함수
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
