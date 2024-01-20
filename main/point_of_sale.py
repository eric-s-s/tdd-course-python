from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


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


class ItemNotFoundError(Exception):
    def __init__(self, *args, barcode: "BarCode"):
        self.barcode = barcode
        super(ItemNotFoundError, self).__init__(*args)

    def __eq__(self, other):
        if not isinstance(other, ItemNotFoundError):
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


@dataclass
class SaleItem:
    price: Price


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


@dataclass
class ShoppingCart:
    _cart: List[SaleItem]

    def __bool__(self):
        return bool(self._cart)

    def update(self, item) -> 'ShoppingCart':
        return ShoppingCart(self._cart + [item])


class AbstractDisplay(ABC):
    @abstractmethod
    def write_item_scanned_message(self, item: SaleItem):
        raise NotImplementedError()

    @abstractmethod
    def write_item_not_found_message(self, error: ItemNotFoundError):
        raise NotImplementedError()

    @abstractmethod
    def write_bad_barcode_message(self, error: BarCodeError):
        raise NotImplementedError()

    @abstractmethod
    def write_no_current_sale_message(self):
        raise NotImplementedError()

    @abstractmethod
    def write_total_sale_price_message(self, shopping_cart: ShoppingCart):
        raise NotImplementedError


class Display(AbstractDisplay):
    def __init__(self):
        self._latest_message: Optional[str] = None

    def get_latest(self) -> Optional[str]:
        return self._latest_message

    def _write(self, message: str):
        self._latest_message = message

    def write_bad_barcode_message(self, error: BarCodeError):
        self._write("Bad barcode. Rescan")

    def write_item_not_found_message(self, error: ItemNotFoundError):
        pass

    def write_item_scanned_message(self, item: SaleItem):
        pass

    def write_no_current_sale_message(self):
        pass

    def write_total_sale_price_message(self, cart: ShoppingCart):
        pass


class AbstractItemLookup(ABC):
    @abstractmethod
    def get_item(self, barcode: BarCode) -> SaleItem:
        raise NotImplementedError()

    @abstractmethod
    def set_item(self, barcode: BarCode, item: SaleItem):
        raise NotImplementedError()


class PointOfSaleSystem:
    def __init__(
        self,
        display: AbstractDisplay,
        lookup: AbstractItemLookup,
        shopping_cart: ShoppingCart,
    ):
        self.display = display
        self.lookup = lookup
        self._shopping_cart = shopping_cart

    @property
    def shopping_cart(self):
        return self._shopping_cart

    @classmethod
    def with_empty_cart(
        cls, display: AbstractDisplay, lookup: AbstractItemLookup
    ) -> "PointOfSaleSystem":
        return cls(display=display, lookup=lookup, shopping_cart=ShoppingCart([]))

    def on_barcode(self, barcode_string: str):
        try:
            barcode = BarCode(barcode_string)
            item = self.lookup.get_item(barcode)
            self._shopping_cart = self.shopping_cart.update(item)
            self.display.write_item_scanned_message(item)
        except BarCodeError as e:
            self.display.write_bad_barcode_message(e)
        except ItemNotFoundError as e:
            self.display.write_item_not_found_message(e)

    def on_total(self):
        if not self._shopping_cart:
            self.display.write_no_current_sale_message()
        else:
            self.display.write_total_sale_price_message(self._shopping_cart)
