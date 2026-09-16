import logging
from datetime import datetime, timezone
from shapely.geometry import Point, Polygon

from app.core.config import settings
from app.sanitizers.base import BaseSanitizer
from app.schemas.measurement import MeasurementSchema


logger = logging.getLogger(__name__)


class GeofenceSanitizer(BaseSanitizer[MeasurementSchema]):
    REGION_POLYGON = Polygon(settings.REGION_POINTS) if (settings.REGION_POINTS and len(settings.REGION_POINTS) >= 3) else None
    MAX_ACCURACY_METERS = 200.0

    def validate(self, item: MeasurementSchema) -> bool:
        if not item.location or self.REGION_POLYGON is None:
            return False

        lat, lon = item.location.latitude, item.location.longitude
        if lat is None or lon is None:
            return False

        if not self.REGION_POLYGON.contains(Point(lon, lat)):
            return False

        if item.location.accuracy < 0 or item.location.accuracy > self.MAX_ACCURACY_METERS:
            return False

        return True
    

class TimestampSanitizer(BaseSanitizer[MeasurementSchema]):
    def validate(self, item: MeasurementSchema) -> bool:
        try:
            dt = datetime.fromisoformat(item.timestamp.replace("Z", "+00:00"))

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)

            if dt > now:
                return False

            if (now - dt).days > 30:
                return False

            return True

        except Exception as e:
            return False


class NetworkQualitySanitizer(BaseSanitizer[MeasurementSchema]):
    def validate(self, item: MeasurementSchema) -> bool:
        if item.internet_quality:
            iq = item.internet_quality
            if (iq.ping is not None and (iq.ping < 0 or iq.ping > 30000)) or (iq.download_mbps is not None and (iq.download_mbps < 0 or iq.download_mbps > 2000)):
                return False
        return True


class AudioSanitizer(BaseSanitizer[MeasurementSchema]):
    MAX_DBFS = 0.0

    def validate(self, item: MeasurementSchema) -> bool:
        if item.noise_measurement:
            nm = item.noise_measurement

            if nm.db is not None:
                if nm.db > self.MAX_DBFS:
                    return False

            if nm.rms is not None and nm.rms < 0:
                return False

        return True