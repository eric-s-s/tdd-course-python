from typing import Dict

import pytest
from point_of_sale import Price

from main.point_of_sale import (AbstractPriceLookup, BarCode, BarCodeError,
                                Display, PointOfSaleSystem, PriceNotFoundError)


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


@pytest.fixture()
def one_twenty_five_barcode():
    return BarCode("2345678901")


@pytest.fixture()
def two_fifty_barcode():
    return BarCode("0987654321")


@pytest.fixture()
def lookup(one_twenty_five_barcode, two_fifty_barcode):
    barcode_to_price = {
        one_twenty_five_barcode: Price(1.25),
        two_fifty_barcode: Price(2.50),
    }
    return FakePriceLookup(barcode_to_price)


@pytest.fixture()
def system(lookup, display):
    return PointOfSaleSystem(display, lookup)


class TestDisplay:
    """Notes: when we get latest, test 0, 1, and many for display calls"""

    def test_get_latest_no_display_calls(self):
        display = Display()
        assert display.get_latest() is None

    def test_get_latest_with_one_message(self):
        message = "some string"
        display = Display()

        display.write(message)

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
    @pytest.fixture(params=["$1.25", "$2.50"], ids=["one twenty five", "two fifty"])
    def barcode_and_expected_string(
        self, request, one_twenty_five_barcode, two_fifty_barcode
    ):
        if request.param == "$1.25":
            yield one_twenty_five_barcode, request.param
        else:
            yield two_fifty_barcode, request.param

    def test_empty_barcode(self, system, display):
        system.on_barcode(barcode_string="")

        result = display.get_latest()
        assert result == "Bad barcode. Rescan"

    def test_bad_barcode(self, system, display):
        system.on_barcode(barcode_string="abc123")

        assert display.get_latest() == "Bad barcode. Rescan"

    def test_no_price_data(self, system, display, lookup):
        missing_barcode_str = "1234509876"
        with pytest.raises(PriceNotFoundError):
            lookup.get_price(BarCode(missing_barcode_str))

        system.on_barcode(missing_barcode_str)

        assert display.get_latest() == f"Item not found: {missing_barcode_str}."

    def test_lookup_found(self, barcode_and_expected_string, display, system):
        barcode, expected = barcode_and_expected_string
        system.on_barcode(barcode.to_string())

        assert display.get_latest() == expected

    def test_lookup_found_with_whitespace(
        self, barcode_and_expected_string, display, system
    ):
        barcode, expected = barcode_and_expected_string
        system.on_barcode(f"  {barcode.to_string()}  ")

        assert display.get_latest() == expected

    @pytest.mark.parametrize("return_character", list("\r\n\t"))
    def test_lookup_with_return_characters(
        self, return_character, display, system, two_fifty_barcode
    ):
        barcode_str = (
            f"{return_character}{two_fifty_barcode.to_string()}{return_character}"
        )

        system.on_barcode(barcode_str)

        assert display.get_latest() == "$2.50"

    def test_lookup_with_all_removed_characters(
        self, display, system, two_fifty_barcode
    ):
        barcode_str = f" \r \t \n {two_fifty_barcode.to_string()} \r \t \n "

        system.on_barcode(barcode_str)

        assert display.get_latest() == "$2.50"


class TestPointOfSaleOnTotal:
    def test_no_items_scanned(self, system, display):
        system.on_total()

        assert display.get_latest() == "No items scanned. No total."

    def test_one_item_scanned(self, system, display, two_fifty_barcode):
        system.on_barcode(two_fifty_barcode.to_string())
        system.on_total()

        assert display.get_latest() == "Total: $2.50"
