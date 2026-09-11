from fastapi import APIRouter

from app.api.v1.endpoints import auth


api_router = APIRouter()

@api_router.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "mobile-sensor-backend"}

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])