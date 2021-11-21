from dataclasses import dataclass
from typing import NewType

Quantity = NewType("Quantity", int)
Sku = NewType("sku", str)  # 실제 사용할 때는 할당받은 Sku로 사용한다.
Reference = NewType("Reference", str)


class TestCustomTypeHinting():
    def __init__(self, ref: Reference, sku: Sku, qty: Quantity):
        self.sku = sku
        self.reference = ref
        self._purchased_quantity = qty


tcth = TestCustomTypeHinting(23, "Hello_sku", "Hello_qty")
print(tcth.sku)
print(tcth.reference)
# _로 시작하는 변수는 Protected 이다.
print(tcth._purchased_quantity)
