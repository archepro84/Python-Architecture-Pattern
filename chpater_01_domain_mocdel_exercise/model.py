from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set

# 동작이 없는 불변 데이터 클래스
@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self.available_quantity = qty

    # 할당이 일어날 때마다 self.available_quantity 값을 감소시킨다.
    def allocate(self, line: OrderLine):
        self.available_quantity -= line.qty