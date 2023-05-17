from unittest.mock import Mock

import pytest

from main.point_of_sale import (
    Display,
    PointOfSaleSystem,
    BarCode,
    BarCodeError,
    AbstractPriceLookup,
    PriceNotFoundError,
)


class FakePriceLookup(AbstractPriceLookup):
    def get(self, barcode: BarCode) -> float:
        return 0.0


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
        with pytest.raises(BarCodeError):
            BarCode("123456789")

    def test_too_long(self):
        with pytest.raises(BarCodeError):
            BarCode("12345678901")

    @pytest.mark.parametrize("bad_char", list("a,.$#:"))
    def test_not_all_digits(self, bad_char):
        with pytest.raises(BarCodeError):
            BarCode(f"1234{bad_char}67890")

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


class TestPointOfSale:
    """
    notes:
    - Xempty, empty
    - Xerror: bad barcode
    - x error: does not exist
    - successful lookup: price
    - success: leading ignored characters
    - success: trailing ignored characters
    - success: leading and trailing ignored characters

    - multiple scans?

    """

    @pytest.fixture
    def barcode_str(self):
        return "0987654321"

    def test_empty_barcode(self):
        display = Display()

        system = PointOfSaleSystem(display, FakePriceLookup())

        system.on_barcode(barcode="")

        result = display.get_latest()
        assert result == ""

    def test_bad_barcode(self):
        display = Display()
        system = PointOfSaleSystem(display, FakePriceLookup())

        system.on_barcode(barcode="abc123")

        assert display.get_latest() == "Bad barcode. Rescan"

    def test_no_price_data(self, barcode_str):
        display = Display()
        lookup = Mock()
        lookup.get.side_effect = PriceNotFoundError("oops")

        system = PointOfSaleSystem(display, lookup)

        system.on_barcode(barcode_str)

        assert display.get_latest() == "Item not found."

    def test_lookup_found(self, barcode_str):
        price = 123.45

        def get(barcode: BarCode):
            if barcode.to_string() == barcode_str:
                return price
            else:
                return 0.0

        lookup = Mock()
        lookup.get = get

        display = Display()
        system = PointOfSaleSystem(display, lookup)
        system.on_barcode(barcode_str)

        assert display.get_latest() == f"${price}"

    def test_lookup_found_with_whitespaces(self, barcode_str):
        price = 123.45

        def get(barcode: BarCode):
            if barcode.to_string() == barcode_str:
                return price
            else:
                return 0.0

        lookup = Mock()
        lookup.get = get

        display = Display()
        system = PointOfSaleSystem(display, lookup)
        system.on_barcode(f"  {barcode_str}  ")

        assert display.get_latest() == f"${price}"
