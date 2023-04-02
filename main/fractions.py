from dataclasses import dataclass, astuple


@dataclass(frozen=True)
class Fraction:
    numerator: int
    denominator: int

    def reduced(self) -> "Fraction":
        if self.numerator == 0:
            return Fraction(0, 1)

        numerator = self.numerator
        denominator = self.denominator
        factor, remainder = divmod(denominator, numerator)
        if remainder == 0:
            numerator = 1
            denominator = factor
        if denominator < 0:
            numerator = -numerator
            denominator = -denominator
        return Fraction(numerator, denominator)
