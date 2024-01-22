from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, TextIO


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
    _cents: int

    @classmethod
    def from_cents(cls, cents: int) -> "Price":
        return cls(_cents=cents)

    @classmethod
    def from_dollars(cls, dollars: float) -> "Price":
        return cls(_cents=int(dollars * 100))

    def __repr__(self):
        return f"{self.__class__.__name__}.from_cents({self._cents})"

    def __add__(self, other) -> "Price":
        if not isinstance(other, Price):
            raise TypeError(f"Tried to add {self.__class__} to {other.__class__}")
        return Price(_cents=self._cents + other._cents)

    def to_display_string(self):
        dollars, cents = divmod(self._cents, 100)
        return f"${dollars:,}.{cents:0>2}"


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

    def update(self, item) -> "ShoppingCart":
        return ShoppingCart(self._cart + [item])

    def get_total(self) -> Price:
        return sum((el.price for el in self._cart), start=Price(0))


class AbstractDisplayFormatter(ABC):
    @abstractmethod
    def item_scanned_message(self, item: SaleItem) -> str:
        raise NotImplementedError()

    @abstractmethod
    def item_not_found_message(self, not_found_error: ItemNotFoundError) -> str:
        raise NotImplementedError()

    @abstractmethod
    def bad_barcode_message(self, barcode_error: BarCodeError) -> str:
        raise NotImplementedError()

    @abstractmethod
    def sale_total_message(self, cart: ShoppingCart) -> str:
        raise NotImplementedError()


class StandardDisplayFormatter(AbstractDisplayFormatter):
    def item_scanned_message(self, item: SaleItem) -> str:
        return f"Item price: {item.price.to_display_string()}"

    def item_not_found_message(self, not_found_error: ItemNotFoundError) -> str:
        return f"No item found for barcode: {not_found_error.barcode.to_string()}"

    def bad_barcode_message(self, barcode_error: BarCodeError) -> str:
        return f"Bad barcode: {barcode_error.barcode_string!r}. Please rescan."

    def sale_total_message(self, cart: ShoppingCart) -> str:
        return f"Total sale: {cart.get_total()}"


class Display:
    def __init__(self, formatter: AbstractDisplayFormatter, stream: TextIO):
        self._formatter = formatter
        self._stream = stream

    def _write_line(self, line):
        stripped_line = line.strip("\n")
        self._stream.write(f"{stripped_line}\n")

    def send_item_scanned(self, item: SaleItem):
        self._write_line(self._formatter.item_scanned_message(item))

    def send_item_not_found(self, error: ItemNotFoundError):
        self._write_line(self._formatter.item_not_found_message(error))

    def send_bad_barcode(self, error: BarCodeError):
        self._write_line(self._formatter.bad_barcode_message(error))

    def send_total_sale_price(self, shopping_cart: ShoppingCart):
        self._write_line(self._formatter.sale_total_message(shopping_cart))


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
        display: Display,
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
        cls, display: Display, lookup: AbstractItemLookup
    ) -> "PointOfSaleSystem":
        return cls(display=display, lookup=lookup, shopping_cart=ShoppingCart([]))

    def on_barcode(self, barcode_string: str):
        try:
            barcode = BarCode(barcode_string)
            item = self.lookup.get_item(barcode)
            self._shopping_cart = self.shopping_cart.update(item)
            self.display.send_item_scanned(item)
        except BarCodeError as e:
            self.display.send_bad_barcode(e)
        except ItemNotFoundError as e:
            self.display.send_item_not_found(e)

    def on_total(self):
        self.display.send_total_sale_price(self._shopping_cart)
