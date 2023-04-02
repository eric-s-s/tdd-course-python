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

same denom
1/5 + 1/5

negatives
-1/5 + 1/5 = 0/1

multiples denom
1/2 + 1/4 = 3/4


"""


class TestFraction:
    def test_fraction_equals_itself(self):
        assert Fraction(2, 3) == Fraction(2, 3)
