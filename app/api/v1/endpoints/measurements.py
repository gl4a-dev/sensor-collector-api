import traceback
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.security import verify_firebase_token
from app.db.session import get_db
from app.schemas.measurement import MeasurementBatchSchema
from app.sanitizers.factory import MeasurementFactory


logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

measurement_factory = MeasurementFactory()


@router.post("/batch", status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_BATCH)
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
            measurement = measurement_factory.create_from_schema(item)
            if measurement:
                new_measurements.append(measurement)

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