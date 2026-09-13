import traceback
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.schemas.measurement import MeasurementBatchSchema
from app.core.security import verify_firebase_token
from app.db.session import get_db
from app.models.measurement import Measurement, WifiNetwork


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
            try:
                m_uuid = uuid.UUID(item.id)
            except (ValueError, AttributeError):
                m_uuid = uuid.uuid4()
            
            timestamp_dt = datetime.fromisoformat(item.timestamp.replace("Z", "+00:00"))

            measurement_entry = Measurement(
                id=m_uuid,
                user_id=user_id,
                timestamp=timestamp_dt,
                latitude=item.location.latitude if item.location else None,
                longitude=item.location.longitude if item.location else None,
                accuracy=item.location.accuracy if item.location else None,
                altitude=item.location.altitude if item.location else None,
                provider=item.location.provider if item.location else None,
                ping=item.internet_quality.ping if item.internet_quality else None,
                jitter=item.internet_quality.jitter if item.internet_quality else None,
                download_mbps=item.internet_quality.download_mbps if item.internet_quality else None,
                upload_mbps=item.internet_quality.upload_mbps if item.internet_quality else None,
                connection_type=item.network_status.connection_type if item.network_status else None,
                connected_ssid=item.network_status.connected_ssid if item.network_status else None,
                connected_bssid=item.network_status.connected_bssid if item.network_status else None,
                noise_db=item.noise_measurement.db if item.noise_measurement else None,
                noise_rms=item.noise_measurement.rms if item.noise_measurement else None,
            )

            if item.wifi_list:
                for wifi in item.wifi_list:
                    wifi_entry = WifiNetwork(
                        measurement_id=m_uuid,
                        ssid=wifi.ssid,
                        bssid=wifi.bssid,
                        rssi=wifi.rssi,
                    )
                    measurement_entry.wifi_networks.append(wifi_entry)

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

        print("=" * 50)
        print("Error processing measurement batch:")
        traceback.print_exc()
        print("=" * 50)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing measurement batch: {str(e)}",
        )