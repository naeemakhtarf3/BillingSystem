from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.session import Base

class PaymentStatus(str, enum.Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    stripe_payment_id = Column(String, nullable=False, unique=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    raw_event = Column(JSON, nullable=True)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
