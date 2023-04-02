from dataclasses import dataclass
from math import gcd


@dataclass(repr=False)
class Fraction:
    numerator: int
    denominator: int

    def __post_init__(self):
        greatest_common_divisor = gcd(self.denominator, self.numerator)
        self.denominator = self.denominator // greatest_common_divisor
        self.numerator = self.numerator // greatest_common_divisor

    def __repr__(self):
        return f"{self.__class__.__name__}({self.numerator}/{self.denominator})"

    def __add__(self, other: "Fraction") -> "Fraction":
        new_dominator = self.denominator * other.denominator
        new_numerator = (
            self.numerator * other.denominator + other.numerator * self.denominator
        )
        return Fraction(new_numerator, new_dominator)
