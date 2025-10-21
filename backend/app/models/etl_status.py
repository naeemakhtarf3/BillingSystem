from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.db.session import Base


class ETLProcessStatus(Base):
    __tablename__ = "etl_process_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    process_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    records_processed = Column(Integer, nullable=False, default=0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


