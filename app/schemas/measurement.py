from typing import List, Optional
from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    latitude: float
    longitude: float
    accuracy: float
    altitude: float
    provider: Optional[str] = None


class InternetQualitySchema(BaseModel):
    ping: Optional[float] = None
    jitter: Optional[float] = None
    ping_success_rate: Optional[float] = None
    download_mbps: Optional[float] = None
    upload_mbps: Optional[float] = None
    started_at: str
    duration_ms: int
    endpoint: str
    success: bool
    error: Optional[str] = None


class NetworkStatusSchema(BaseModel):
    connection_type: str
    connected_ssid: Optional[str] = None
    connected_bssid: Optional[str] = None
    is_metered: bool = False
    has_internet: bool = False
    is_validated: bool = False
    mobile_operator: Optional[str] = None
    mobile_country_code: Optional[str] = None
    mobile_network_code: Optional[str] = None


class WifiNetworkSchema(BaseModel):
    ssid: str
    bssid: str
    rssi: int


class NoiseMeasurementSchema(BaseModel):
    rms: Optional[float] = None
    db: Optional[float] = None


class MeasurementSchema(BaseModel):
    id: str
    timestamp: str
    location: Optional[LocationSchema] = None
    internet_quality: Optional[InternetQualitySchema] = None
    network_status: Optional[NetworkStatusSchema] = None
    wifi_list: Optional[List[WifiNetworkSchema]] = None
    noise_measurement: Optional[NoiseMeasurementSchema] = None


class MeasurementBatchSchema(BaseModel):
    measurements: List[MeasurementSchema] = Field(..., min_items=1, max_items=100)