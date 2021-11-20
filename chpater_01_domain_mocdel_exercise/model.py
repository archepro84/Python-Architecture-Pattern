# document : https://www.cosmicpython.com/book/chapter_01_domain_model.html
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


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(
            b for b in sorted(batches) if b.can_allocate(line)
        )
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        # Set을 사용하여 집합 안에 있는 원소는 모두 유일하다.
        self._allocations: Set[OrderLine] = set()  # _allocations 변수는 OrderLine 데이터 클래스를 참조한다.

    # Equal Magic Method
    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    # doc : https://oreil.ly/YUzg5
    # 객체를 집합에 추가하거나 Dictionary의 Key로 사용할 때 동작을 제어하기 위한 Magic Method
    def __hash__(self):
        return hash(self.reference)

    # sorted()를 작동하게 하기 위한 Magic Method
    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    # Batch._purchased_quantity - Set에 저장된 모든 OrderLine.qty 값을 뺀 결과값
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


    def test_allocation_is_idempotent():
        batch, line = make_batch_and_line_fixture("ANGULAR-DESK", 20, 2)
        batch.allocate(line)
        batch.allocate(line)
        assert batch.available_quantity == 18


    def chapter1_test_1_3():
        large_batch, small_line = make_batch_and_line_fixture("ELEGANT-LAMP", 20, 2)
        print(large_batch.can_allocate(small_line))
        print(large_batch.can_allocate(small_line))
        test_allocation_is_idempotent()


    # chapter1_test_1_3()
    pass
