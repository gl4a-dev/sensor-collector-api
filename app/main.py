from fastapi import FastAPI

from app.api.v1.router import api_router


app = FastAPI(
    title="Sensor Collector API",
    description="Authentication and Sensor Collector Backend",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Sensor Collector API is running."}