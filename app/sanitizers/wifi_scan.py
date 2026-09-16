from typing import Optional
from app.models.measurement import WifiScan
from app.sanitizers.base import BaseFactory, BaseSanitizer
from app.schemas.measurement import WifiNetworkSchema


class HotspotSanitizer(BaseSanitizer[WifiNetworkSchema]):
    MOBILE_ONLY_OUIS = {
        "00:cd:fe", "f4:0f:24", "bc:d1:d3", # Apple
        "50:01:d9", "cc:6e:a4", "ec:1f:72", # Samsung
        "d8:ce:3a", "e8:b4:c8", # Google Pixel
    }

    def validate(self, item: WifiNetworkSchema) -> bool:
        if not item.bssid:
            return False

        clean_bssid = item.bssid.replace(":", "").replace("-", "").strip().lower()

        if len(clean_bssid) < 12:
            return False

        # 1.  Filtering by LAA bit
        if clean_bssid[1] in {'2', '3', '6', '7', 'a', 'b', 'e', 'f'}:
            return False

        # 2. Filtering by OUI
        formatted_oui = f"{clean_bssid[0:2]}:{clean_bssid[2:4]}:{clean_bssid[4:6]}"
        if formatted_oui in self.MOBILE_ONLY_OUIS:
            return False

        return True


class WifiScanFactory(BaseFactory[WifiNetworkSchema, WifiScan]):
    def __init__(self):
        self.chain = HotspotSanitizer()

    def create(self, item: WifiNetworkSchema) -> Optional[WifiScan]:
        if not self.chain.handle(item):
            return None

        return WifiScan(bssid=item.bssid, rssi=item.rssi)