import random
import string
from typing import Dict

import pytest

from main.point_of_sale import (AbstractPriceLookup, BarCode, BarCodeError,
                                Display, PointOfSaleSystem, Price,
                                PriceNotFoundError)


class FakePriceLookup(AbstractPriceLookup):
    def __init__(self, barcode_to_price: Dict[BarCode, Price]):
        self._mapping = {k: v for k, v in barcode_to_price.items()}

    def get_price(self, barcode: BarCode) -> float:
        if barcode not in self._mapping:
            raise PriceNotFoundError(f"{barcode!r} not in lookup")
        return self._mapping[barcode]


@pytest.fixture()
def display():
    return Display()


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


class TestDisplay:
    """Notes: when we get latest, test 0, 1, and many for display calls"""

    def test_get_latest_no_display_calls(self):
        display = Display()
        assert display.get_latest() is None

    def test_get_latest_with_one_message(self):
        message = "some string"
        display = Display()

        display._write(message)

        assert display.get_latest() == message


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


class TestPointOfSaleScanSingleItem:
    @pytest.mark.parametrize(
        "bad_barcode", ["", "bad code"], ids=["empty", "malformed"]
    )
    def test_empty_barcode(self, display, bad_barcode):
        system = PointOfSaleSystem(display, FakePriceLookup({}))
        system.on_barcode(barcode_string=bad_barcode)

        result = display.get_latest()
        assert result == "Bad barcode. Rescan"

    def test_no_price_data(self, display):
        lookup = FakePriceLookup({get_random_barcode(): Price(123)})
        with pytest.raises(PriceNotFoundError):
            lookup.get_price(get_random_barcode())

        system = PointOfSaleSystem(display, lookup)

        missing_barcode_str = get_random_barcode().to_string()
        system.on_barcode(missing_barcode_str)

        assert display.get_latest() == f"Item not found: {missing_barcode_str}."

    @pytest.mark.parametrize(
        "price, expected", [(Price(1234.5), "$1,234.50"), (Price(2.34), "$2.34")]
    )
    def test_lookup_found(self, display, price, expected):
        barcode = get_random_barcode()
        lookup = FakePriceLookup({get_random_barcode(): Price(498574), barcode: price})
        system = PointOfSaleSystem(display, lookup)

        system.on_barcode(barcode.to_string())

        assert display.get_latest() == expected

    @pytest.mark.parametrize("extra_character", list(" \r\n\t"))
    def test_lookup_found_with_extra_character(self, display, extra_character):
        barcode = get_random_barcode()
        price = Price(12)
        lookup = FakePriceLookup({get_random_barcode(): Price(498574), barcode: price})
        system = PointOfSaleSystem(display, lookup)

        system.on_barcode(
            f"{extra_character*2}{barcode.to_string()}{extra_character*2}"
        )

        assert display.get_latest() == "$12.00"

    def test_lookup_with_all_removed_characters(self, display):
        barcode = get_random_barcode()
        price = Price(3.21)
        lookup = FakePriceLookup({get_random_barcode(): Price(498574), barcode: price})
        system = PointOfSaleSystem(display, lookup)
        barcode_str = f" \r \t \n {barcode.to_string()} \r \t \n "

        system.on_barcode(barcode_str)

        assert display.get_latest() == "$3.21"


class TestPointOfSaleOnTotal:
    def test_no_items_scanned(self, display):
        system = PointOfSaleSystem(display, FakePriceLookup({}))
        system.on_total()

        assert display.get_latest() == "No items scanned. No total."

    def test_one_item_scanned(self, display):
        barcode = get_random_barcode()
        lookup = FakePriceLookup({barcode: Price(23.45)})
        system = PointOfSaleSystem(display, lookup)

        system.on_barcode(barcode.to_string())
        system.on_total()

        assert display.get_latest() == "Total: $23.45"

    def test_two_items_scanned(self, display):
        three_fifty = get_random_barcode()
        two_fifteen = get_random_barcode()
        lookup = FakePriceLookup({three_fifty: Price(3.5), two_fifteen: Price(2.15)})
        system = PointOfSaleSystem(display, lookup)

        system.on_barcode(three_fifty.to_string())
        system.on_barcode(two_fifteen.to_string())
        system.on_total()

        assert display.get_latest() == "Total: $5.65"

    def test_two_items_scanned_and_missing_bar_code(self, display):
        prices = [Price(12.34), Price(2348.7)]
        barcodes = [get_random_barcode(), get_random_barcode()]
        lookup = FakePriceLookup(dict(zip(barcodes, prices)))
        system = PointOfSaleSystem(display, lookup)

        system.on_barcode(barcodes[0].to_string())
        system.on_barcode(get_random_barcode().to_string())
        system.on_barcode(barcodes[1].to_string())
        system.on_total()

        expected = f"Total: $2,361.04"
        assert display.get_latest() == expected

    def test_two_items_scanned_and_bad(self, display):
        prices = [Price(234.3), Price(1.23)]
        barcodes = [get_random_barcode(), get_random_barcode()]
        lookup = FakePriceLookup(dict(zip(barcodes, prices)))
        system = PointOfSaleSystem(display, lookup)

        system.on_barcode(barcodes[0].to_string())
        system.on_barcode("oooops")
        system.on_barcode(barcodes[1].to_string())
        system.on_total()

        expected = f"Total: $235.53"
        assert display.get_latest() == expected
