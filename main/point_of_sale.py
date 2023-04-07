from typing import Optional


class Display:
    def __init__(self):
        self.latest_message: Optional[str] = None

    def get_latest(self) -> Optional[str]:
        return self.latest_message

    def write(self, message: str):
        self.latest_message = message


class PointOfSaleSystem:
    def __init__(self, display: Display):
        self.display = display

    def on_barcode(self, barcode: str):
        self.display.write("")
