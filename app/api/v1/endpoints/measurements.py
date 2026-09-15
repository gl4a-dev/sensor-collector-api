import traceback
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.wifi_sanitizer import is_mobile_hotspot
from app.core.geofence import is_inside_region
from app.core.security import verify_firebase_token
from app.db.session import get_db
from app.schemas.measurement import MeasurementBatchSchema
from app.models.measurement import Measurement, MobileConnection, WifiConnection, WifiScan


logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def receive_measurement_batch(
    request: Request,
    batch: MeasurementBatchSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_firebase_token),
):
    """
    Receives a batch of measurements sent by the mobile app. Validates authentication via Firebase Token and saves the batch to the database.
    """
    try:
        user_id = current_user.get("uid") or current_user.get("sub")
        new_measurements = []

        for item in batch.measurements:
            lat = item.location.latitude if item.location else None
            lon = item.location.longitude if item.location else None
            if not is_inside_region(lon=lon, lat=lat):
                continue

            try:
                m_uuid = uuid.UUID(item.id)
            except (ValueError, AttributeError):
                m_uuid = uuid.uuid4()

            timestamp_dt = datetime.fromisoformat(
                item.timestamp.replace("Z", "+00:00")
            )

            measurement_entry = Measurement(
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


            if (item.network_status) and (item.network_status.connection_type == "wifi"):
                measurement_entry.wifi_connection = WifiConnection(
                    connected_ssid=item.network_status.connected_ssid,
                    connected_bssid=item.network_status.connected_bssid,
                )

            
            elif (item.network_status) and (item.network_status.connection_type == "mobile"):
                measurement_entry.mobile_connection = MobileConnection(
                    mobile_operator=item.network_status.mobile_operator,
                    mobile_country_code=item.network_status.mobile_country_code,
                    mobile_network_code=item.network_status.mobile_network_code,
                )


            if item.wifi_list:
                for wifi in item.wifi_list:
                    if is_mobile_hotspot(wifi.bssid):
                        continue

                    scan_entry = WifiScan(
                        bssid=wifi.bssid,
                        rssi=wifi.rssi,
                    )
                    measurement_entry.wifi_scans.append(scan_entry)

            new_measurements.append(measurement_entry)

        db.add_all(new_measurements)
        db.commit()

        return {
            "status": "success",
            "message": f"{len(new_measurements)} measurements recorded.",
            "user_id": user_id,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error processing measurement batch: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing measurement batch: {str(e)}",
        )