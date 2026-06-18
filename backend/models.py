from sqlalchemy import Column, Integer, Float, DateTime, Boolean
from datetime import datetime
from .database import Base


class GasReading(Base):
    __tablename__ = "gas_readings"

    id = Column(Integer, primary_key=True, index=True)
    co_ppm = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class FanStatus(Base):
    __tablename__ = "fan_status"

    id = Column(Integer, primary_key=True, index=True)
    is_running = Column(Boolean, default=False)
    auto_mode = Column(Boolean, default=True)
    threshold_ppm = Column(Float, default=50.0)
    updated_at = Column(DateTime, default=datetime.utcnow)
