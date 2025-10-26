from sqlalchemy import Column, ForeignKey, String, Text, func, BIGINT, Boolean
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from DB.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(BIGINT, primary_key=True, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # MODIFIED: Content is now nullable
    content = Column(Text, nullable=True) 
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # --- ADD THESE THREE LINES ---
    media_url = Column(String(255), nullable=True)
    message_type = Column(String(50), nullable=False, default='text') # e.g., 'text', 'image', 'video'
    is_read = Column(Boolean, default=False, nullable=False)

    # Relationships to easily access the User objects from a Message
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")
