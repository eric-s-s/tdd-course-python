from typing import Optional


class Display:
    def __init__(self):
        self.thing = None

    def get_latest(self) -> Optional[str]:
        return self.thing

    def write(self, thing: str):
        self.thing = thing


class PointOfSaleSystem:
    def __init__(self, display: Display):
        pass

    def on_barcode(self, barcode: str):
        pass
