import pytest

from main.point_of_sale import (
    AbstractPriceLookup,
    BarCode,
    BarCodeError,
    Display,
    PointOfSaleSystem,
    PriceNotFoundError,
)

ONE_TWENTY_FIVE = BarCode("1234567890")
TWO_FIFTY = BarCode("0987654321")


class FakePriceLookup(AbstractPriceLookup):
    def get(self, barcode: BarCode) -> float:
        mapping = {
            ONE_TWENTY_FIVE: 1.25,
            TWO_FIFTY: 2.5,
        }
        if barcode not in mapping:
            raise PriceNotFoundError(f"{barcode!r} not in lookup")
        return mapping[barcode]


@pytest.fixture(scope="session")
def lookup():
    return FakePriceLookup()


@pytest.fixture(scope="session")
def display():
    return Display()


@pytest.fixture(scope="session")
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

    def test_empty_barcode(self, system, display):
        system.on_barcode(barcode="")

        result = display.get_latest()
        assert result == "Bad barcode. Rescan"

    def test_bad_barcode(self, system, display):
        system.on_barcode(barcode="abc123")

        assert display.get_latest() == "Bad barcode. Rescan"

    def test_no_price_data(self, system, display, lookup):
        missing_barcode_str = "1234509876"
        with pytest.raises(PriceNotFoundError):
            lookup.get(BarCode(missing_barcode_str))

        system.on_barcode(missing_barcode_str)

        assert display.get_latest() == f"Item not found: {missing_barcode_str}."

    @pytest.mark.parametrize(
        "barcode, expected",
        [
            (TWO_FIFTY, "$2.50"),
            (ONE_TWENTY_FIVE, "$1.25"),
        ],
    )
    def test_lookup_found(self, barcode, expected, display, system):
        system.on_barcode(barcode.to_string())

        assert display.get_latest() == expected

    @pytest.mark.parametrize(
        "barcode, expected",
        [
            (TWO_FIFTY, "$2.50"),
            (ONE_TWENTY_FIVE, "$1.25"),
        ],
    )
    def test_lookup_found_with_whitespace(self, barcode, expected, display, system):
        system.on_barcode(f"  {barcode.to_string()}  ")

        assert display.get_latest() == expected

    @pytest.mark.parametrize("return_character", list("\r\n\t"))
    def test_lookup_with_return_characters(self, return_character, display, system):
        barcode_str = f"{return_character}{TWO_FIFTY.to_string()}{return_character}"

        system.on_barcode(barcode_str)

        assert display.get_latest() == "$2.50"

    def test_lookup_with_all_removed_characters(self, display, system):
        barcode_str = f" \r \t \n {TWO_FIFTY.to_string()} \r \t \n "

        system.on_barcode(barcode_str)

        assert display.get_latest() == "$2.50"
