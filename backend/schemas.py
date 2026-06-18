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


class FanStatusBase(BaseModel):
    is_running: bool
    auto_mode: bool
    threshold_ppm: float


class FanStatusUpdate(BaseModel):
    is_running: Optional[bool] = None
    auto_mode: Optional[bool] = None
    threshold_ppm: Optional[float] = None


class FanStatus(FanStatusBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True
