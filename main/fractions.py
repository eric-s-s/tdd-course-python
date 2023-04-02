from dataclasses import dataclass, astuple
from math import gcd


@dataclass(frozen=True)
class Fraction:
    numerator: int
    denominator: int

    def reduced(self) -> "Fraction":
        if self.numerator == 0:
            return Fraction(0, 1)

        numerator = self.numerator
        denominator = self.denominator
        if denominator < 0:
            numerator = -numerator
            denominator = -denominator

        factor = gcd(numerator, denominator)
        numerator //= factor
        denominator //= factor
        return Fraction(numerator, denominator)

    def __eq__(self, other):
        return astuple(self.reduced()) == astuple(other.reduced())

    def __hash__(self):
        return hash(astuple(self.reduced()))

    def __add__(self, other: "Fraction") -> "Fraction":
        numerator = (
            self.numerator * other.denominator + other.numerator * self.denominator
        )
        denominator = self.denominator * other.denominator
        return Fraction(numerator, denominator).reduced()
