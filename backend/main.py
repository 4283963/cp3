import asyncio
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import engine, SessionLocal, Base, get_db
from . import models, schemas
from .sensor import sensor

Base.metadata.create_all(bind=engine)

app = FastAPI(title="有毒气体监控系统", description="CO浓度监控与风机联动系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_fan_device(db: Session):
    fan = db.query(models.FanDevice).first()
    if not fan:
        fan = models.FanDevice(
            name="1号排风机",
            device_code="FAN-001",
            is_running=False,
            auto_mode=True,
            threshold_ppm=50.0,
            location="主作业区",
            updated_at=datetime.utcnow()
        )
        db.add(fan)
        db.commit()
        db.refresh(fan)
        print(f"[初始化] 风机设备已创建: {fan.name} ({fan.device_code}) | 位置: {fan.location} | 阈值: {fan.threshold_ppm} ppm")
    return fan


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        init_fan_device(db)
    finally:
        db.close()
    asyncio.create_task(sensor_monitor_task())


async def sensor_monitor_task():
    while True:
        db = SessionLocal()
        try:
            co_ppm = sensor.read()
            db_reading = models.GasReading(co_ppm=co_ppm)
            db.add(db_reading)

            fan = db.query(models.FanDevice).first()
            if fan:
                if fan.auto_mode:
                    should_run = co_ppm >= fan.threshold_ppm
                    if fan.is_running != should_run:
                        old_status = "ON" if fan.is_running else "OFF"
                        new_status = "ON" if should_run else "OFF"
                        fan.is_running = should_run
                        fan.updated_at = datetime.utcnow()
                        if should_run:
                            print(f"[联动触发] CO浓度 {co_ppm:.2f} ppm >= 阈值 {fan.threshold_ppm} ppm | 风机 {fan.device_code} 自动启动: {old_status} -> {new_status}")
                        else:
                            print(f"[联动触发] CO浓度 {co_ppm:.2f} ppm < 阈值 {fan.threshold_ppm} ppm | 风机 {fan.device_code} 自动停止: {old_status} -> {new_status}")
                else:
                    if co_ppm >= fan.threshold_ppm and not fan.is_running:
                        print(f"[联动警告] CO浓度 {co_ppm:.2f} ppm >= 阈值 {fan.threshold_ppm} ppm，但风机 {fan.device_code} 处于手动模式未启动！建议立即手动开启！")

            db.commit()
        except Exception as e:
            print(f"传感器监控任务错误: {e}")
        finally:
            db.close()
        await asyncio.sleep(3)


@app.get("/api/readings/latest", response_model=List[schemas.GasReading])
def get_latest_readings(db: Session = Depends(get_db)):
    readings = db.query(models.GasReading).order_by(
        models.GasReading.timestamp.desc()
    ).limit(10).all()
    return list(reversed(readings))


@app.get("/api/readings/current", response_model=schemas.GasReading)
def get_current_reading(db: Session = Depends(get_db)):
    reading = db.query(models.GasReading).order_by(
        models.GasReading.timestamp.desc()
    ).first()
    if not reading:
        raise HTTPException(status_code=404, detail="暂无数据")
    return reading


@app.get("/api/fan", response_model=schemas.FanDevice)
def get_fan_status(db: Session = Depends(get_db)):
    fan = db.query(models.FanDevice).first()
    if not fan:
        fan = init_fan_device(db)
    return fan


@app.put("/api/fan", response_model=schemas.FanDevice)
def update_fan_status(fan_update: schemas.FanDeviceUpdate, db: Session = Depends(get_db)):
    fan = db.query(models.FanDevice).first()
    if not fan:
        fan = init_fan_device(db)

    if fan_update.is_running is not None:
        old_status = "ON" if fan.is_running else "OFF"
        new_status = "ON" if fan_update.is_running else "OFF"
        fan.is_running = fan_update.is_running
        print(f"[手动操作] 风机 {fan.device_code} 手动切换: {old_status} -> {new_status}")

    if fan_update.auto_mode is not None:
        fan.auto_mode = fan_update.auto_mode
        mode_text = "自动" if fan_update.auto_mode else "手动"
        print(f"[手动操作] 风机 {fan.device_code} 切换为{mode_text}模式")

    if fan_update.threshold_ppm is not None:
        fan.threshold_ppm = fan_update.threshold_ppm
        print(f"[手动操作] 风机 {fan.device_code} 阈值更新为 {fan_update.threshold_ppm} ppm")

    fan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(fan)
    return fan


@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
