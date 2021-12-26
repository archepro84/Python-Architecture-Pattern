from __future__ import annotations
from typing import Optional
from datetime import date

from domain import model
from domain.model import OrderLine
from adapters.repository import AbstractRepository


# 단순히 테스트에서 의존성을 제거할 수 있다는 이유만으로 새로운 서비스를 작성해야 할까?
def add_batch(
    ref: str,
    sku: str,
    qty: int,
    eta: Optional[date],
    repo: AbstractRepository,
    session,
) -> None:
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()


# 이전: allocate는 도메인 객체를 받는다.
#  def allocate(line:OrderLine, repo: AbstractRepository, session) -> str:

# 이후: allocate는 문자열과 정수를 받는다
#  함수의 파라미터를 모두 원시타입으로 변경
def allocate(
    orderid: str, sku: str, qty: int, repo: AbstractRepository, session
) -> str:
    line = OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref
