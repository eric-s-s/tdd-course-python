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

    def test_greatest_common_denominator(self):
        assert_reduced(Fraction(15, 40), Fraction(3, 8))

    def test_greatest_common_denominator_negative_numerator(self):
        assert_reduced(Fraction(-12, 9), Fraction(-4, 3))

    def test_greatest_common_denominator_negative_denominator(self):
        assert_reduced(Fraction(49, -35), Fraction(-7, 5))


class TestFractionsEquality:
    def test_zero(self):
        assert Fraction(0, -2) == Fraction(-0, 25) == Fraction(0, 1)

    def test_greatest_common_denominator(self):
        assert Fraction(2, 3) == Fraction(-10, -15) == Fraction(6, 9)

    def test_inequality(self):
        assert Fraction(1, 2) != Fraction(-1, 2)


class TestFractionsHash:
    def test_zero(self):
        assert hash(Fraction(0, -2)) == hash(Fraction(-0, 25)) == hash(Fraction(0, 1))

    def test_greatest_common_denominator(self):
        assert hash(Fraction(2, 3)) == hash(Fraction(-10, -15)) == hash(Fraction(6, 9))

    def test_inequality(self):
        assert hash(Fraction(1, 2)) != hash(Fraction(-1, 2))


def assert_exact_match(fraction, numerator, denominator):
    assert astuple(fraction) == (numerator, denominator)


class TestAdd:
    def test_add_zeros(self):
        actual = Fraction(0, 2) + Fraction(0, 3)
        assert_exact_match(actual, 0, 1)

    @pytest.mark.parametrize("fraction", [Fraction(1, 2), Fraction(-3, 2)])
    def test_add_zero_no_change(self, fraction):
        assert Fraction(0, 1) + fraction == fraction
        assert fraction + Fraction(0, 1) == fraction

    def test_add_zero_reduces_other(self):
        result = Fraction(-6, -15) + Fraction(0, -1)
        assert_exact_match(result, 2, 5)

    def test_add_same_denominator(self):
        result = Fraction(-1, 3) + Fraction(-2, 3)
        assert_exact_match(result, -1, 1)

    def test_add_similar_denominator(self):
        result = Fraction(-2, -3) + Fraction(1, 6)
        assert_exact_match(result, 5, 6)
