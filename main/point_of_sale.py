from typing import Optional
from dataclasses import dataclass


class BarCodeError(Exception):
    pass


class PriceNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class BarCode:
    _value: str

    def __post_init__(self):
        expected_len = 10
        if len(self.to_string()) != expected_len:
            raise BarCodeError("Bar code should be 10 digits")
        if not self.to_string().isdigit():
            raise BarCodeError("Bar code contains non digits")

    def to_string(self) -> str:
        return self._value.strip()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_string()})"

    def __eq__(self, other):
        if isinstance(other, BarCode):
            return self.to_string() == other.to_string()
        return False


class Display:
    def __init__(self):
        self.latest_message: Optional[str] = None

    def get_latest(self) -> Optional[str]:
        return self.latest_message

    def write(self, message: str):
        self.latest_message = message


class AbstractPriceLookup:
    def get(self, barcode: BarCode) -> float:
        raise NotImplementedError()


class PointOfSaleSystem:
    def __init__(self, display: Display, lookup: AbstractPriceLookup):
        self.display = display
        self.lookup = lookup

    def on_barcode(self, barcode: str):
        if not barcode:
            self.display.write("")
            return

        try:
            barcode = BarCode(barcode)
        except BarCodeError:
            self.display.write("Bad barcode. Rescan")
            return
