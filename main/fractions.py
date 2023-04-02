from dataclasses import dataclass, astuple


@dataclass(frozen=True)
class Fraction:
    numerator: int
    denominator: int

    def reduced(self) -> "Fraction":
        if self.numerator == 0:
            return Fraction(0, 1)
        return self

    def __eq__(self, other: "Fraction") -> bool:
        return astuple(self.reduced()) == astuple(other.reduced())

    def __hash__(self):
        return hash(astuple(self.reduced()))
