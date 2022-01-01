from __future__ import annotations
from typing import Optional
from datetime import date

from allocation.domain import model
from allocation.domain.model import OrderLine
from allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str,
    sku: str,
    qty: int,
    eta: Optional[date],
    uow: unit_of_work.AbstractUnitOfWork,  # Service Layer의 의존성은 UoW 추상화 하나뿐
):
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(
    orderid: str,
    sku: str,
    qty: int,
    uow: unit_of_work.AbstractUnitOfWork,  # Service Layer의 의존성은 UoW 추상화 하나뿐
) -> str:
    line = OrderLine(orderid, sku, qty)
    with uow:  # Conect Manager로 UoW를 실행
        batches = (
            uow.batches.list()
        )  # Batch Repository, UoW는 영속적 Repository에 대한 접근을 제공한다.
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = model.allocate(line, batches)
        uow.commit()  # 작업이 끝나면 UoW를 사용해 Commit or Rollback한다.
    return batchref
