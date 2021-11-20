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
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()  # _allocations 변수는 OrderLine 데이터 클래스를 참조한다.

    
    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty


# 테스트 코드의 디버깅을 하기 위한 Main
if __name__ == '__main__':
    def make_batch_and_line_fixture(sku, batch_qty, line_qty):
        return (
            Batch("batch-001", sku, batch_qty, eta=date.today()),
            OrderLine("order-123", sku, line_qty),
        )


    def chapter1_test_1():
        large_batch, small_line = make_batch_and_line_fixture("ELEGANT-LAMP", 20, 2)
        print(large_batch.can_allocate(small_line))
        print(large_batch.can_allocate(small_line))


    chapter1_test_1()
