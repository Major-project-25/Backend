# Backend/model/post.py

import uuid
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from DB.base import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=True)
    media_url = Column(String(255), nullable=True)
    content_type = Column(String(50), nullable=False)  # 'text', 'image', 'video'
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)