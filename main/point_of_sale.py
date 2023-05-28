from dataclasses import dataclass
from typing import Optional


class BarCodeError(Exception):
    pass


class PriceNotFoundError(Exception):
    pass


@dataclass
class Price:
    _value: float

    def __repr__(self):
        return f"{self.__class__.__name__}({self._value})"

    def to_display_string(self):
        return f"${self._value:.2f}"


class Stringifiable:
    def to_string(self):
        raise NotImplementedError()


class DummyBarcode(Stringifiable):
    def to_string(self):
        return "EMPTY"


class BarCode(Stringifiable):
    def __init__(self, barcode_str: str):
        to_use = barcode_str.strip()
        self._value = to_use
        self._validate()

    def to_string(self):
        return self._value

    def _validate(self):
        expected_len = 10
        if not self.to_string():
            raise BarCodeError("No input.")
        if len(self.to_string()) != expected_len:
            msg = f"Bad barcode: {self.to_string()}. Should be ten digits."
            raise BarCodeError(msg)
        if not self.to_string().isdigit():
            msg = f"Bad barcode: {self.to_string()}. Should only contain digits."
            raise BarCodeError(msg)

    def __eq__(self, other):
        if isinstance(other, BarCode):
            return self.to_string() == other.to_string()
        return False

    def __hash__(self):
        return hash(self.to_string())

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_string()})"


class Display:
    def __init__(self):
        self.latest_message: Optional[str] = None

    def get_latest(self) -> Optional[str]:
        return self.latest_message

    def write(self, message: str):
        self.latest_message = message

    def write_bad_barcode_message(self):
        self.write("Bad barcode. Rescan")

    def write_price_not_found_message(self, barcode: Stringifiable):
        self.write(f"Item not found: {barcode.to_string()}.")

    def write_price_message(self, price: Price):
        self.write(price.to_display_string())


class AbstractPriceLookup:
    def get_price(self, barcode: BarCode) -> Price:
        raise NotImplementedError()


class PointOfSaleSystem:
    def __init__(self, display: Display, lookup: AbstractPriceLookup):
        self.display = display
        self.lookup = lookup

    def on_barcode(self, barcode_string: str):
        barcode = DummyBarcode()
        try:
            barcode = BarCode(barcode_string)
            price = self.lookup.get_price(barcode)
            self.display.write_price_message(price)
        except BarCodeError:
            self.display.write_bad_barcode_message()
        except PriceNotFoundError:
            self.display.write_price_not_found_message(barcode)
