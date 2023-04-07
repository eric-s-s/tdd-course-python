from typing import Optional


class Display:
    def get_latest(self) -> Optional[str]:
        return None


class PointOfSaleSystem:
    def __init__(self, display: Display):
        pass

    def on_barcode(self, barcode: str):
        pass
