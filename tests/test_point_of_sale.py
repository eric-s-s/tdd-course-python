class Display:
    def get_latest(self):
        return ""


class PointOfSaleSystem:
    def __init__(self, display: Display):
        pass

    def on_barcode(self, barcode: str):
        pass


def test_empty_barcode():
    display = Display()

    system = PointOfSaleSystem(display)

    system.on_barcode(barcode="")

    result = display.get_latest()
    assert result == ""
