from typing import Optional


class BarCodeError(Exception):
    pass


class PriceNotFoundError(Exception):
    pass


class BarCode:
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


class AbstractPriceLookup:
    def get(self, barcode: BarCode) -> float:
        raise NotImplementedError()


class PointOfSaleSystem:
    def __init__(self, display: Display, lookup: AbstractPriceLookup):
        self.display = display
        self.lookup = lookup

    def on_barcode(self, barcode: str):
        display_message = self.get_display_message(barcode)
        self.display.write(display_message)

    def get_display_message(self, barcode_str: str) -> str:
        try:
            barcode = BarCode(barcode_str)
        except BarCodeError:
            return "Bad barcode. Rescan"

        try:
            price = self.lookup.get(barcode)
        except PriceNotFoundError:
            return f"Item not found: {barcode.to_string()}."

        return f"${price:.2f}"
