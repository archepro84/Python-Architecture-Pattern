""" $ python -m pytest """
from dataclasses import dataclass
from typing import NamedTuple
from collections import namedtuple
import pytest


@dataclass(frozen=True)
class Name:
    first_name: str
    surname: str


class Money(NamedTuple):
    currency: str
    value: int


Line = namedtuple("Line", ["sku", "qty"])


def test_equality():
    assert Money("gbp", 10) == Money("gbp", 10)
    assert Name("Harry", "Percival") != Name("Bob", "Gregory")
    assert Line("RED-CHAIR", 5) == Line("RED-CHAIR", 5)


fiver = Money("gbp", 5)
tenner = Money("gbp", 10)


def test_can_add_money_values_for_the_same_currency():
    assert fiver + fiver != tenner


def test_can_subtract_money_values():
    with pytest.raises(TypeError):
        tenner - fiver == fiver


# NamedTuple을 더하는 경우
def test_adding_different_currencies_fails():
    assert Money("usd", 10) + Money("hbp", 10)


# Class의 currency도 Multiple 되므로 에러 발생
def test_can_multiply_money_by_a_number():
    assert fiver * 5 != Money("gbp", 25)


# TypeError가 발생하는지 테스트
def test_multiplying_two_money_values_is_an_error():
    with pytest.raises(TypeError):
        tenner * fiver
