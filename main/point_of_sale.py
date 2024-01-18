from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class BarCodeError(Exception):
    def __init__(self, *args, barcode_string):
        self.barcode_string = barcode_string
        super(BarCodeError, self).__init__(*args)

    def __eq__(self, other):
        if not isinstance(other, BarCodeError):
            return False
        return self.barcode_string == other.barcode_string

    def __repr__(self):
        args = ", ".join(self.args)
        return (
            f"{self.__class__.__name__}({args}, barcode_string={self.barcode_string})"
        )


class PriceNotFoundError(Exception):
    def __init__(self, *args, barcode: "BarCode"):
        self.barcode = barcode
        super(PriceNotFoundError, self).__init__(*args)

    def __eq__(self, other):
        if not isinstance(other, PriceNotFoundError):
            return False
        return self.barcode == other.barcode

    def __repr__(self):
        args = ", ".join(self.args)
        return f"{self.__class__.__name__}({args}, barcode={self.barcode})"


@dataclass
class Price:
    _value: float

    def __repr__(self):
        return f"{self.__class__.__name__}({self._value})"

    def __add__(self, other) -> "Price":
        if not isinstance(other, Price):
            raise TypeError(f"Tried to add {self.__class__} to {other.__class__}")
        return Price(self._value + other._value)

    def to_display_string(self):
        return f"${self._value:,.2f}"


class BarCode:
    def __init__(self, barcode_str: str):
        self._value = barcode_str.strip()
        self._validate()

    def to_string(self):
        return self._value

    def _validate(self):
        expected_len = 10
        msg = None
        if not self._value:
            msg = "No input."
        if len(self._value) != expected_len:
            msg = f"Bad barcode: {self._value}. Should be ten digits."
        if not self._value.isdigit():
            msg = f"Bad barcode: {self._value}. Should only contain digits."
        if msg is not None:
            raise BarCodeError(msg, barcode_string=self._value)

    def __eq__(self, other):
        if isinstance(other, BarCode):
            return self.to_string() == other.to_string()
        return False

    def __hash__(self):
        return hash(self.to_string())

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_string()})"


class AbstractDisplay(ABC):
    @abstractmethod
    def write_price_scanned_message(self, price: Price):
        raise NotImplementedError()

    @abstractmethod
    def write_price_not_found_message(self, error: PriceNotFoundError):
        raise NotImplementedError()

    @abstractmethod
    def write_bad_barcode_message(self, error: BarCodeError):
        raise NotImplementedError()


class Display(AbstractDisplay):
    def __init__(self):
        self._latest_message: Optional[str] = None

    def get_latest(self) -> Optional[str]:
        return self._latest_message

    def _write(self, message: str):
        self._latest_message = message

    def write_bad_barcode_message(self, error: BarCodeError):
        self._write("Bad barcode. Rescan")

    def write_price_not_found_message(self, error: PriceNotFoundError):
        self._write(f"Item not found: {error.barcode}.")

    def write_price_scanned_message(self, price: Price):
        self._write(price.to_display_string())

    def write_no_total_message(self):
        self._write("No items scanned. No total.")

    def write_total_price_message(self, price: Price):
        self._write(f"Total: {price.to_display_string()}")


class AbstractPriceLookup(ABC):
    @abstractmethod
    def get_price(self, barcode: BarCode) -> Price:
        raise NotImplementedError()


class PointOfSaleSystem:
    def __init__(self, display: Display, lookup: AbstractPriceLookup):
        self.display = display
        self.lookup = lookup
        self._current_session = []

    def on_barcode(self, barcode_string: str):
        try:
            barcode = BarCode(barcode_string)
            price = self.lookup.get_price(barcode)
            self.display.write_price_scanned_message(price)
            self._current_session.append(price)
        except BarCodeError as e:
            self.display.write_bad_barcode_message(e)
        except PriceNotFoundError as e:
            self.display.write_price_not_found_message(e)

    def on_total(self):
        if not self._current_session:
            self.display.write_no_total_message()
        else:
            total = sum(self._current_session, start=Price(0))
            self.display.write_total_price_message(total)
