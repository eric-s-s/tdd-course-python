import sys
from queue import Queue, Empty

from point_of_sale import (
    BarCode,
    Display,
    InMemoryLookup,
    PointOfSaleSystem,
    Price,
    SaleItem,
    StandardDisplayFormatter, ScannerListener, Seconds,
)

display = Display(formatter=StandardDisplayFormatter(), stream=sys.stdout)
lookup = InMemoryLookup(
    {
        BarCode("1234567890"): SaleItem(price=Price.from_dollars(12.23)),
        BarCode("1234567891"): SaleItem(price=Price.from_dollars(1.05)),
        BarCode("1234567892"): SaleItem(price=Price.from_dollars(10.50)),
        BarCode("1234567893"): SaleItem(price=Price.from_dollars(100.3)),
    }
)
system = PointOfSaleSystem.with_empty_cart(display=display, lookup=lookup)

queue = Queue()

listener = ScannerListener(sys.stdin, system, Seconds(0.1))


if __name__ == "__main__":
    print("hello")
    system.on_total()

    with listener.start():
        while True:
            input("gimme barcode >>> ")
            try:
                system.on_barcode(queue.get(timeout=0.5))
            except Empty:
                pass
            system.on_total()

    # system.on_barcode("1234567890")
    # system.on_barcode("1234567899")
    # system.on_barcode("1234567891")
    # system.on_barcode("1234567892")
    # system.on_barcode("1234567893")
    # system.on_barcode("1234567893")
