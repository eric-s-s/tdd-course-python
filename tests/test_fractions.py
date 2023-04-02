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


class TestFraction:
    def test_fraction_equals_itself(self):
        assert Fraction(2, 3) == Fraction(2, 3)
