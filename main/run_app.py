import sys
from io import StringIO
from threading import Thread, Event
from typing import TextIO

from point_of_sale import (
    PointOfSaleSystem,
    Display,
    StandardDisplayFormatter,
    BarCode,
    SaleItem,
    Price,
    InMemoryLookup,
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

class MyListener:
    def __init__(self, input_stream: TextIO, pos_system: PointOfSaleSystem):
        self._intput_stream = input_stream
        self._system = pos_system

    def run(self):
        data = self._intput_stream.readline()
        print(f"READ: {data}\n")
        if not data:
            return

        if "total" in data:
            print("asked for total")
            self._system.on_total()
        else:
            print("DATA")
            self._system.on_barcode(data)


if __name__ == "__main__":
    print("hello")
    system.on_total()
    listener = MyListener(sys.stdin, system)
    while True:
        listener.run()


    # system.on_barcode("1234567890")
    # system.on_barcode("1234567899")
    # system.on_barcode("1234567891")
    # system.on_barcode("1234567892")
    # system.on_barcode("1234567893")
    # system.on_barcode("1234567893")
