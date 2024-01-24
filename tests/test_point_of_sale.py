import random
import string
from typing import Dict
from unittest.mock import Mock
from io import StringIO

import pytest

from main.point_of_sale import (
    AbstractItemLookup,
    BarCode,
    BarCodeError,
    PointOfSaleSystem,
    Price,
    ShoppingCart,
    SaleItem,
    StandardDisplayFormatter,
    Display,
    AbstractDisplayFormatter,
    ItemNotFoundError,
    InMemoryLookup,
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
        assert Price.from_dollars(value).to_display_string() == expected_string

    def test_to_string_with_cents(self):
        cents = 1_234_50
        assert Price.from_cents(cents).to_display_string() == "$1,234.50"


class TestShoppingCart:
    def test_empty_cart_get_total(self):
        assert ShoppingCart([]).get_total() == Price.from_dollars(0)

    def test_one_item_get_total(self):
        price = Price.from_dollars(1232343)
        assert ShoppingCart([SaleItem(price=price)]).get_total() == price

    def test_many_items_get_total(self):
        first_price = Price.from_dollars(1.1)
        second_price = Price.from_dollars(2.2)
        third_price = Price.from_dollars(3.3)
        assert ShoppingCart(
            [
                SaleItem(price=first_price),
                SaleItem(price=second_price),
                SaleItem(price=third_price),
            ]
        ).get_total() == Price.from_dollars(6.6)


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


class TestDisplayFormatter:
    @pytest.fixture
    def formatter(self):
        return StandardDisplayFormatter()

    def test_item_scanned(self, formatter):
        price = Price.from_cents(123)
        item = SaleItem(price=price)

        assert (
            formatter.item_scanned_message(item)
            == f"Item price: {price.to_display_string()}"
        )

    def test_item_not_found(self, formatter):
        barcode = get_random_barcode()

        expected = f"No item found for barcode: {barcode.to_string()}"
        assert (
            formatter.item_not_found_message(ItemNotFoundError("oops", barcode=barcode))
            == expected
        )

    def test_bad_barcode(self, formatter):
        barcode_string = "not a barcode"

        expected = f"Bad barcode: {barcode_string!r}. Please rescan."
        assert (
            formatter.bad_barcode_message(
                BarCodeError("oops", barcode_string=barcode_string)
            )
            == expected
        )

    def test_total_sale(self, formatter):
        cart = ShoppingCart([SaleItem(price=Price.from_cents(12_32))])

        expected = f"Total sale: $12.32"
        assert formatter.sale_total_message(cart) == expected


class MockDisplayFormatter(AbstractDisplayFormatter):
    def item_scanned_message(self, item: SaleItem) -> str:
        return str(item)

    def item_not_found_message(self, not_found_error: ItemNotFoundError) -> str:
        return str(not_found_error.barcode)

    def bad_barcode_message(self, barcode_error: BarCodeError) -> str:
        return barcode_error.barcode_string

    def sale_total_message(self, cart: ShoppingCart) -> str:
        return str(cart)


class TestDisplay:
    @pytest.fixture
    def stream(self):
        return StringIO()

    @pytest.fixture
    def display(self, stream) -> Display:
        return Display(formatter=MockDisplayFormatter(), stream=stream)

    def test_initial_display_has_no_messages(self, display, stream):
        stream.seek(0)
        assert stream.read() == ""

    def test_send_item_scanned(self, display, stream):
        item = SaleItem(price=(Price.from_dollars(123.34)))
        display.send_item_scanned(item)

        stream.seek(0)
        assert stream.read() == f"{item}\n"

    def test_send_item_not_found(self, display, stream):
        barcode = get_random_barcode()

        display.send_item_not_found(ItemNotFoundError("ooops", barcode=barcode))

        stream.seek(0)
        assert stream.read() == f"{barcode}\n"

    def test_send_bad_barcode(self, display, stream):
        bad_barcode = "this is not a legal barcode string"

        display.send_bad_barcode(BarCodeError("nuts!", barcode_string=bad_barcode))

        stream.seek(0)
        assert stream.read() == f"{bad_barcode}\n"

    def test_send_total_sale_message(self, display, stream):
        cart = ShoppingCart(
            [SaleItem(price=Price.from_cents(1)), SaleItem(price=Price.from_cents(2))]
        )
        display.send_total_sale_price(cart)

        stream.seek(0)
        assert stream.read() == f"{cart}\n"


class TestItemLookup:
    @staticmethod
    def generate_catalog_using(mapping: Dict[BarCode, SaleItem]) -> AbstractItemLookup:
        return InMemoryLookup(mapping)

    def test_get_item_no_item(self):
        barcode = get_random_barcode()
        lookup = self.generate_catalog_using({})
        with pytest.raises(ItemNotFoundError) as exec_info:
            lookup.get_item(barcode)

        assert exec_info.value.barcode == barcode

    def test_get_item_found_item(self):
        barcode = get_random_barcode()
        item = SaleItem(price=Price.from_cents(123))

        lookup = self.generate_catalog_using(
            {
                get_random_barcode(): SaleItem(price=Price.from_cents(345)),
                barcode: item,
                get_random_barcode(): SaleItem(price=Price.from_cents(3454)),
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
    return Mock(spec=Display)


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

        mock_display.send_item_scanned.assert_called_once_with(item)

    @pytest.mark.parametrize(
        "bad_barcode", ["", "bad code"], ids=["empty", "malformed"]
    )
    def test_bad_barcode(self, system, mock_display, bad_barcode):
        system.on_barcode(barcode_string=bad_barcode)

        expected = BarCodeError(
            "message is ignored in testing", barcode_string=bad_barcode
        )
        mock_display.send_bad_barcode.assert_called_once_with(expected)

    def test_no_price_data_displays_missing_price(
        self, system, mock_display, mock_lookup
    ):
        barcode = get_random_barcode()
        error = ItemNotFoundError("oops", barcode=barcode)

        mock_lookup.get_item.side_effect = error

        system.on_barcode(get_random_barcode().to_string())

        mock_display.send_item_not_found.assert_called_once_with(error)

    def test_lookup_called_correctly(self, mock_lookup, system):
        barcode = get_random_barcode()

        system.on_barcode(barcode.to_string())

        mock_lookup.get_item.assert_called_once_with(barcode)

    def test_adds_looked_up_item_to_cart(self, mock_lookup, system):
        assert system.shopping_cart == ShoppingCart([])

        item = SaleItem(price=Price.from_cents(3458934534))
        mock_lookup.get_item.return_value = item

        system.on_barcode(get_random_barcode().to_string())

        assert system.shopping_cart == ShoppingCart([item])


class TestPointOfSaleOnTotal:
    @pytest.mark.parametrize(
        "cart",
        [
            ShoppingCart([SaleItem(price=Price.from_cents(123))]),
            ShoppingCart(
                [
                    SaleItem(price=Price.from_cents(123)),
                    SaleItem(price=Price.from_cents(456)),
                ]
            ),
            ShoppingCart([SaleItem(price=Price.from_cents(el)) for el in range(1, 10)]),
        ],
    )
    def test_write_current_sale(self, mock_display, cart):
        system = PointOfSaleSystem(mock_display, Mock(), shopping_cart=cart)

        system.on_total()

        mock_display.send_total_sale_price.assert_called_once_with(cart)
