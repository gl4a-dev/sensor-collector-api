from typing import Optional
from app.models.measurement import WifiConnection
from app.sanitizers.base import BaseFactory, BaseSanitizer
from app.schemas.measurement import NetworkStatusSchema


class WifiConnectionSanitizer(BaseSanitizer[NetworkStatusSchema]):
    def validate(self, item: NetworkStatusSchema) -> bool:
        if not item.connected_bssid and not item.connected_ssid:
            return False
        return True


class WifiConnectionFactory(BaseFactory[NetworkStatusSchema, WifiConnection]):
    def __init__(self):
        self.chain = WifiConnectionSanitizer()

    def create(self, item: NetworkStatusSchema) -> Optional[WifiConnection]:
        if not self.chain.handle(item):
            return None

        return WifiConnection(
            connected_ssid=item.connected_ssid,
            connected_bssid=item.connected_bssid,
        )