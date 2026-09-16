import uuid
from datetime import datetime
from typing import Optional

from app.models.measurement import Measurement
from app.schemas.measurement import MeasurementSchema
from app.sanitizers.measurement import AudioSanitizer, GeofenceSanitizer, NetworkQualitySanitizer, TimestampSanitizer
from app.sanitizers.mobile_connection import MobileConnectionFactory
from app.sanitizers.wifi_connection import WifiConnectionFactory
from app.sanitizers.wifi_scan import WifiScanFactory


class MeasurementFactory:
    def __init__(self):
        self.chain = GeofenceSanitizer(
            next_sanitizer=TimestampSanitizer(
                next_sanitizer=NetworkQualitySanitizer(
                    next_sanitizer=AudioSanitizer()
                )
            )
        )

        self.wifi_scan_factory = WifiScanFactory()
        self.wifi_connection_factory = WifiConnectionFactory()
        self.mobile_connection_factory = MobileConnectionFactory()

    def create_from_schema(self, item: MeasurementSchema) -> Optional[Measurement]:
        if not self.chain.handle(item):
            return None

        try:
            m_uuid = uuid.UUID(item.id)
        except (ValueError, AttributeError):
            m_uuid = uuid.uuid4()

        timestamp_dt = datetime.fromisoformat(item.timestamp.replace("Z", "+00:00"))

        measurement = Measurement(
            id=m_uuid,
            timestamp=timestamp_dt,
            latitude=item.location.latitude if item.location else None,
            longitude=item.location.longitude if item.location else None,
            accuracy=item.location.accuracy if item.location else None,
            altitude=item.location.altitude if item.location else None,
            connection_type=item.network_status.connection_type if item.network_status else "none",
            has_internet=item.network_status.has_internet if item.network_status else False,
            ping=item.internet_quality.ping if item.internet_quality else None,
            jitter=item.internet_quality.jitter if item.internet_quality else None,
            ping_success_rate=item.internet_quality.ping_success_rate if item.internet_quality else None,
            download_mbps=item.internet_quality.download_mbps if item.internet_quality else None,
            upload_mbps=item.internet_quality.upload_mbps if item.internet_quality else None,
            test_success=item.internet_quality.success if item.internet_quality else None,
            noise_db=item.noise_measurement.db if item.noise_measurement else None,
            noise_rms=item.noise_measurement.rms if item.noise_measurement else None,
        )

        if item.network_status:
            if item.network_status.connection_type == "wifi":
                measurement.wifi_connection = self.wifi_connection_factory.create(item.network_status)
            elif item.network_status.connection_type == "mobile":
                measurement.mobile_connection = self.mobile_connection_factory.create(item.network_status)

        if item.wifi_list:
            for wifi_schema in item.wifi_list:
                scan_model = self.wifi_scan_factory.create(wifi_schema)
                if scan_model:
                    measurement.wifi_scans.append(scan_model)

        return measurement