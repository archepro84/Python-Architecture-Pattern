from __future__ import annotations

import model
from model import OrderLine
from repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()  # 저장소에서 객체들을 가져온다.
    if not is_valid_sku(line.sku, batches):  # 해당하는 요청을 검사하거나 assertion으로 검증한다.
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)  # Domain 서비스를 초훌한다.
    session.commit()  # 모든 단계가 정상으로 실행됐다면 변경한 상태를 저장하거나 업데이트한다.
    return batchref
