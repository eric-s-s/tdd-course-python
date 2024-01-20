import random
import string
from typing import Dict, Optional
from unittest.mock import Mock

import pytest

from main.point_of_sale import (
    AbstractItemLookup,
    BarCode,
    BarCodeError,
    PointOfSaleSystem,
    Price,
    ItemNotFoundError,
    AbstractDisplay,
    ShoppingCart,
    SaleItem,
)


def get_random_barcode():
    code_digits = "".join(random.choice(string.digits) for _ in range(10))
    return BarCode(code_digits)


class TestPrice:
    @pytest.mark.parametrize(
        "value, expected_string",
        [
            (0.0, "$0.00"),
            (0.1, "$0.10"),
            (0.02, "$0.02"),
            (1.0, "$1.00"),
            (1.1, "$1.10"),
            (1.23, "$1.23"),
            (12.3, "$12.30"),
            (1_234.5, "$1,234.50"),
            (12_345_678.9, "$12,345,678.90"),
        ],
    )
    def test_to_string(self, value, expected_string):
        assert Price(value).to_display_string() == expected_string


class TestShoppingCart:
    def test_empty_cart_get_total(self):
        assert ShoppingCart([]).get_total() == Price(0)

    def test_one_item_get_total(self):
        price = Price(1232343)
        assert ShoppingCart([SaleItem(price=price)]).get_total() == price

    def test_many_items_get_total(self):
        first_price = Price(1.1)
        second_price = Price(2.2)
        third_price = Price(3.3)
        assert ShoppingCart(
            [
                SaleItem(price=first_price),
                SaleItem(price=second_price),
                SaleItem(price=third_price),
            ]
        ).get_total() == Price(6.6)


class DisplayImplementation(AbstractDisplay):
    def __init__(self):
        self._latest = None

    def get_latest(self) -> Optional[str]:
        return self._latest

    def write_item_scanned_message(self, item: SaleItem):
        self._latest = f"Item Price: {item.price.to_display_string()}"

    def write_item_not_found_message(self, error: ItemNotFoundError):
        self._latest = f"No item found for: {error.barcode.to_string()}"

    def write_bad_barcode_message(self, error: BarCodeError):
        self._latest = f"Please rescan. Bad barcode: {error.barcode_string}"

    def write_no_current_sale_message(self):
        self._latest = "No sale in progress."

    def write_total_sale_price_message(self, shopping_cart: ShoppingCart):
        self._latest = f"Total: {shopping_cart.get_total().to_display_string()}"


class TestDisplayContract:
    @staticmethod
    def get_display() -> "AbstractDisplay":
        return DisplayImplementation()

    @pytest.fixture
    def display(self) -> "AbstractDisplay":
        return self.get_display()

    def test_initial_display_has_no_messages(self, display):
        assert display.get_latest() is None

    def test_write_item_scanned(self, display):
        price = Price(123.34)

        display.write_item_scanned_message(SaleItem(price=price))

        assert price.to_display_string() in display.get_latest()

    def test_write_item_not_found(self, display):
        barcode = get_random_barcode()

        display.write_item_not_found_message(
            ItemNotFoundError("ooops", barcode=barcode)
        )

        assert barcode.to_string() in display.get_latest()

    def test_write_bad_barcode(self, display):
        bad_barcode = "this is not a legal barcode string"

        display.write_bad_barcode_message(
            BarCodeError("nuts!", barcode_string=bad_barcode)
        )

        assert bad_barcode in display.get_latest()

    def test_write_no_sale_message(self, display):
        display.write_no_current_sale_message()

        assert "No sale in progress" in display.get_latest()

    def test_write_total_sale_message(self, display):
        cart = ShoppingCart([SaleItem(price=Price(1)), SaleItem(price=Price(2))])
        display.write_total_sale_price_message(cart)

        assert cart.get_total().to_display_string() in display.get_latest()
        assert "Total" in display.get_latest()


class TestBarcode:
    def test_barcode_correctly_formatted(self):
        barcode_str = "0983454321"
        assert BarCode(barcode_str).to_string() == barcode_str

    def test_too_short(self):
        barcode_string = "123456789"
        with pytest.raises(BarCodeError):
            BarCode(barcode_string)

    def test_too_long(self):
        barcode_str = "12345678901"
        with pytest.raises(BarCodeError):
            BarCode(barcode_str)

    def test_empty(self):
        with pytest.raises(BarCodeError):
            BarCode("")

    @pytest.mark.parametrize("bad_char", list("a,.#:"))
    def test_not_all_digits(self, bad_char):
        barcode_str = f"1234{bad_char}67890"
        with pytest.raises(BarCodeError):
            BarCode(barcode_str)

    def test_removes_whitespace_to_string(self):
        barcode_str = "2398470982"
        assert (
            BarCode(barcode_str).to_string()
            == BarCode(f"  {barcode_str}  ").to_string()
            == barcode_str
        )

    def test_removes_whitespace_equality(self):
        barcode_str = "0987654321"
        assert BarCode(barcode_str) == BarCode(f"  {barcode_str} ")

    def test_all_whitespace_characters(self):
        barcode_string = get_random_barcode().to_string()
        assert BarCode(f" \t \n \r {barcode_string} \r \n  \t  ") == BarCode(
            barcode_string
        )


class LookupImplementationForTesting(AbstractItemLookup):
    def __init__(self, lookup: Dict[BarCode, SaleItem]):
        self._lookup = lookup

    def get_item(self, barcode: BarCode) -> SaleItem:
        try:
            return self._lookup[barcode]
        except KeyError:
            raise ItemNotFoundError("oops", barcode=barcode)

    def set_item(self, barcode: BarCode, item: SaleItem):
        self._lookup[barcode] = item


class TestItemLookup:
    @staticmethod
    def generate_catalog_using(mapping: Dict[BarCode, SaleItem]) -> AbstractItemLookup:
        return LookupImplementationForTesting(mapping)

    def test_get_item_no_item(self):
        barcode = get_random_barcode()
        with pytest.raises(ItemNotFoundError) as exec_info:
            self.generate_catalog_using({}).get_item(barcode)

        assert exec_info.value.barcode == barcode

    def test_get_item_found_item(self):
        barcode = get_random_barcode()
        item = SaleItem(price=Price(123))

        lookup = self.generate_catalog_using(
            {
                get_random_barcode(): SaleItem(price=Price(345)),
                barcode: item,
                get_random_barcode(): SaleItem(price=Price(3454)),
            }
        )

        assert lookup.get_item(barcode) == item

    def test_set_item(self):
        barcode = get_random_barcode()
        item = Mock()
        lookup = self.generate_catalog_using({})

        lookup.set_item(barcode=barcode, item=item)

        assert lookup.get_item(barcode) == item


@pytest.fixture
def mock_display():
    return Mock(spec=AbstractDisplay)


@pytest.fixture
def mock_lookup():
    return Mock(spec=AbstractItemLookup)


@pytest.fixture
def system(mock_lookup, mock_display):
    return PointOfSaleSystem.with_empty_cart(display=mock_display, lookup=mock_lookup)


class TestPointOfSaleScanSingleItem:
    def test_on_barcode_writes_item_from_lookup(
        self, system, mock_lookup, mock_display
    ):
        item = Mock()
        mock_lookup.get_item.return_value = item

        system.on_barcode(get_random_barcode().to_string())

        mock_display.write_item_scanned_message.assert_called_once_with(item)

    @pytest.mark.parametrize(
        "bad_barcode", ["", "bad code"], ids=["empty", "malformed"]
    )
    def test_bad_barcode(self, system, mock_display, bad_barcode):
        system.on_barcode(barcode_string=bad_barcode)

        expected = BarCodeError(
            "message is ignored in testing", barcode_string=bad_barcode
        )
        mock_display.write_bad_barcode_message.assert_called_once_with(expected)

    def test_no_price_data_displays_missing_price(
        self, system, mock_display, mock_lookup
    ):
        barcode = get_random_barcode()
        error = ItemNotFoundError("oops", barcode=barcode)

        mock_lookup.get_item.side_effect = error

        system.on_barcode(get_random_barcode().to_string())

        mock_display.write_item_not_found_message.assert_called_once_with(error)

    def test_lookup_called_correctly(self, mock_lookup, system):
        barcode = get_random_barcode()

        system.on_barcode(barcode.to_string())

        mock_lookup.get_item.assert_called_once_with(barcode)

    def test_adds_looked_up_item_to_cart(self, mock_lookup, system):
        assert system.shopping_cart == ShoppingCart([])

        item = SaleItem(price=Price(3458934534))
        mock_lookup.get_item.return_value = item

        system.on_barcode(get_random_barcode().to_string())

        assert system.shopping_cart == ShoppingCart([item])


class TestPointOfSaleOnTotal:
    def test_no_items_scanned_writes_no_total_message(self, mock_display):
        system = PointOfSaleSystem(mock_display, Mock(), shopping_cart=ShoppingCart([]))
        system.on_total()

        mock_display.write_no_current_sale_message.assert_called_once_with()

    @pytest.mark.parametrize(
        "cart",
        [
            ShoppingCart([SaleItem(price=Price(123))]),
            ShoppingCart([SaleItem(price=Price(123)), SaleItem(price=Price(456))]),
            ShoppingCart([SaleItem(price=Price(el)) for el in range(1, 10)]),
        ],
    )
    def test_write_current_sale(self, mock_display, cart):
        system = PointOfSaleSystem(mock_display, Mock(), shopping_cart=cart)

        system.on_total()

        mock_display.write_total_sale_price_message.assert_called_once_with(cart)
