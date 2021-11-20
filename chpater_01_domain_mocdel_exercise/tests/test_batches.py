from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set

from model import Batch, OrderLine


# 성공하는 테스트 케이스
def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


# Batch와 OrderLine 클래스를 Return하는 fixture 역할
def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty),
    )


# 할당받은 Batch, OrderLine이 정상적으로 호출되었는지 테스트 (can_allocate)
def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)


# 할당받은 Batch, OrderLine이 정상적으로 호출되었는지 테스트 (can_allocate)
def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False


# 할당받은 Batch, OrderLine이 정상적으로 호출되었는지 테스트 (can_allocate)
def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)


# 할당받은 Batch, OrderLine이 정상적으로 호출되었는지 테스트 (can_allocate)
def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False


# 라인에 할당되지 않은 Batch를 해제하면 Batch의 가용 수량에 아무 영향이 없어야한다.
def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


# Batch._allocations에 저장된 Set의 모든 OrderLine.qty 값을
#  Batch._purchased_quantity에 뺀 결과값과 일치하는지 테스트
#  Batch 클래스에 중복된 OrderLine이 삽입되어도 집합으로 중복 제거가 되는지 테스트
def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18
