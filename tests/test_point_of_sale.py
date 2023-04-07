from main.point_of_sale import Display, PointOfSaleSystem


def test_empty_barcode():
    display = Display()

    system = PointOfSaleSystem(display)

    system.on_barcode(barcode="")

    result = display.get_latest()
    assert result == ""
