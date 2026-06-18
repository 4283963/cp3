from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GasReadingBase(BaseModel):
    co_ppm: float


class GasReadingCreate(GasReadingBase):
    pass


class GasReading(GasReadingBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class FanDeviceBase(BaseModel):
    is_running: bool
    auto_mode: bool
    threshold_ppm: float


class FanDeviceUpdate(BaseModel):
    is_running: Optional[bool] = None
    auto_mode: Optional[bool] = None
    threshold_ppm: Optional[float] = None


class FanDevice(FanDeviceBase):
    id: int
    name: str
    device_code: str
    location: str
    updated_at: datetime

    class Config:
        from_attributes = True
