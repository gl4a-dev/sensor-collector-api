from typing import Optional

from app.models.measurement import MobileConnection
from app.sanitizers.base import BaseSanitizer, BaseFactory
from app.schemas.measurement import NetworkStatusSchema


class MobileConnectionSanitizer(BaseSanitizer[NetworkStatusSchema]):
    def validate(self, item: NetworkStatusSchema) -> bool:
        return True


class MobileConnectionFactory(BaseFactory[NetworkStatusSchema, MobileConnection]):
    def __init__(self):
        self.chain = MobileConnectionSanitizer()

    def create(self, item: NetworkStatusSchema) -> Optional[MobileConnection]:
        if not self.chain.handle(item):
            return None

        return MobileConnection(
            mobile_operator=item.mobile_operator,
            mobile_country_code=item.mobile_country_code,
            mobile_network_code=item.mobile_network_code,
        )