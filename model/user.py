from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, ARRAY,SmallInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from DB.base import Base
import uuid
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    university_reg_no = Column(String(50), unique=True, nullable=True)
    biography = Column(Text, nullable=True)
    
    # New columns for interests and their weights
    interest1 = Column(String(50), nullable=True)
    interest1_weight = Column(SmallInteger, nullable=True)
    interest2 = Column(String(50), nullable=True)
    interest2_weight = Column(SmallInteger, nullable=True)
    interest3 = Column(String(50), nullable=True)
    interest3_weight = Column(SmallInteger, nullable=True)
    matched_profiles = Column(ARRAY(UUID(as_uuid=True)), default=[])

    is_admin = Column(Boolean, default=False)

    # Relationships to messages
    messages_sent = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver")