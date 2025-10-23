# Backend/model/post_reaction.py

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from DB.base import Base

class PostReaction(Base):
    __tablename__ = "post_reactions"

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    reaction_type = Column(String(10), nullable=False) # 'like' or 'dislike'
