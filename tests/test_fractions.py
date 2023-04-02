from dataclasses import astuple

import pytest

from main.fractions import Fraction

# TODO write notes and then make better tests

"""
notes:

0 + 0
0 + 1
2 + 0

1 + 2
-1 + 2
neg plus neg

reduction
0/4 to 0/1
0/-5 to 0/1

-1/3 to -1/3
1/-3 to -1/3
-1/-3 to 1/3

2/4 to 1/2
8/16 to 1/2
2/6 to 1/3
-2/6 to -1/3


same denom
1/5 + 1/5

negatives
-1/5 + 1/5 = 0/1

multiples denom
1/2 + 1/4 = 3/4


"""


def assert_equals(a, b):
    assert a == b, (a.reduced(), b.reduced())


def assert_hash_equal(a, b):
    assert hash(a) == hash(b), (a.reduced(), b.reduced())


@pytest.fixture(params=[assert_equals, assert_hash_equal], ids=["eq", "hash"])
def equality_assertion(request):
    yield request.param


def assert_reduced(to_reduce, expected):
    assert astuple(to_reduce.reduced()) == astuple(expected)


class TestFractionReduced:
    def test_fraction_equals_itself(self):
        assert_reduced(Fraction(2, 3), Fraction(2, 3))

    def test_zero_numerator(self):
        assert_reduced(Fraction(0, 5), Fraction(0, 1))

    @pytest.mark.parametrize(
        "negative", [Fraction(0, -45), Fraction(-0, 2), Fraction(-0, -23423)]
    )
    def test_zero_numerator_with_negatives(self, negative):
        assert_reduced(negative, Fraction(0, 1))

    def test_single_negative(self):
        assert_reduced(Fraction(1, -3), Fraction(-1, 3))

    def test_double_negative(self):
        assert_reduced(Fraction(-2, -11), Fraction(2, 11))

    def test_simple_division(self):
        assert_reduced(Fraction(4, 16), Fraction(1, 4))

    def test_simple_division_negative(self):
        assert_reduced(Fraction(4, -16), Fraction(-1, 4))

    def test_simple_division_negative_numerator(self):
        assert_reduced(Fraction(-25, 125), Fraction(-1, 5))
