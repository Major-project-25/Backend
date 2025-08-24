from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from DB.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    university_reg_no = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    biography = Column(Text)
    interest1 = Column(String(50))
    interest2 = Column(String(50))
    interest3 = Column(String(50))
    matched_profiles = Column(ARRAY(UUID(as_uuid=True)), default=[])
