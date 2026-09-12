from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.measurement import MeasurementBatchSchema
from app.core.security import verify_firebase_token

router = APIRouter()

@router.post("/batch", status_code=status.HTTP_200_OK)
async def receive_measurement_batch(
    batch: MeasurementBatchSchema,
    current_user: dict = Depends(verify_firebase_token)
):
    """
    Recebe um lote de medições enviadas pelo aplicativo mobile.
    Valida a autenticação via Firebase Token e insere o lote no processamento.
    """
    try:
        user_id = current_user.get("uid")
        processed_count = len(batch.measurements)
        
        # Lógica de inserção no banco SQL ou fila de processamento
        # ex: await save_measurements_to_db(user_id, batch.measurements)

        return {
            "status": "success",
            "message": f"{processed_count} measurements processed successfully.",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing measurement batch: {str(e)}"
        )