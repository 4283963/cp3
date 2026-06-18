from sqlalchemy import Column, Integer, Float, DateTime, Boolean, String
from datetime import datetime
from .database import Base


class GasReading(Base):
    __tablename__ = "gas_readings"

    id = Column(Integer, primary_key=True, index=True)
    co_ppm = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class FanDevice(Base):
    __tablename__ = "fan_devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="1号排风机")
    device_code = Column(String(50), nullable=False, unique=True, default="FAN-001")
    is_running = Column(Boolean, default=False)
    auto_mode = Column(Boolean, default=True)
    threshold_ppm = Column(Float, default=50.0)
    location = Column(String(200), default="主作业区")
    updated_at = Column(DateTime, default=datetime.utcnow)
