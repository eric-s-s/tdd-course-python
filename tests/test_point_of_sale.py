import pytest

from main.point_of_sale import Display, PointOfSaleSystem


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


class TestPointOfSale:
    """
    notes:
    - empty, empty
    - error: bad barcode
    - error: does not exist
    - error: price response is NaN
    - empty, error
    - successful lookup: price
    - success: leading ignored characters
    - success: trailing ignored characters
    - success: leading and trailing ignored characters

    - multiple scans?

    """
    def test_empty_barcode(self):
        display = Display()

        system = PointOfSaleSystem(display)

        system.on_barcode(barcode="")

        result = display.get_latest()
        assert result == ""
