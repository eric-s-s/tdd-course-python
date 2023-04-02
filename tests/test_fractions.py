from fractions import Fraction


class TestFractions:
    def test_equality(self):
        assert Fraction(1, 2) == Fraction(1, 2)

    def test_string(self):
        assert str(Fraction(1, 2)) == "1/2"

    def test_repr(self):
        assert repr(Fraction(1, 2)) == "Fraction(1/2)"

    def test_reduces_numerator_divisible_by_denominator(self):
        assert repr(Fraction(3, 9)) == "Fraction(1/3)"

    def test_reduces_by_greatest_common_divisor(self):
        assert repr(Fraction(4, 6)) == "Fraction(2/3)"

    def test_add_with_same_numerator(self):
        first = Fraction(1, 4)
        second = Fraction(2, 4)
        expected = Fraction(3, 4)
        assert first + second == expected

    def test_add_with_different_denominator_simple_multiple(self):
        first = Fraction(1, 4)
        second = Fraction(1, 2)
        expected = Fraction(3, 4)
        assert first + second == expected

    def test_add_with_different_denominator_no_common_multiple(self):
        # 1/3 + 1/4 = 7/12
        first = Fraction(1, 4)
        second = Fraction(1, 3)
        expected = Fraction(7, 12)
        assert first + second == expected

    def test_add_with_common_multiple(self):
        # 5/6 + 3/4 = 10/12 + 9/12 = 19/12
        first = Fraction(5, 6)
        second = Fraction(3, 4)
        expected = Fraction(19, 12)
        assert first + second == expected
