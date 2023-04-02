from fractions import Fraction


class TestFractions:
    def test_equality(self):
        assert Fraction(1, 1) == Fraction(1, 2)
