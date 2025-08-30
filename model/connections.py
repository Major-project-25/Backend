# model/connections.py

from sqlalchemy import Column, ForeignKey, String, func, TIMESTAMP # Import TIMESTAMP here
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from DB.base import Base

class Connection(Base):
    __tablename__ = "connections"

    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    addressee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    
    status = Column(String(20), nullable=False, default='pending')
    
    # Use TIMESTAMP(timezone=True) for TIMESTAMPTZ
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships to get user objects
    requester = relationship("User", foreign_keys=[requester_id])
    addressee = relationship("User", foreign_keys=[addressee_id])