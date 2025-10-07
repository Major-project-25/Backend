# Backend/repositories/post_repo.py

from sqlalchemy.orm import Session
from uuid import UUID
from model.post import Post
from typing import List

def create_post(db: Session, author_id: UUID, content: str, media_url: str, content_type: str) -> Post:
    db_post = Post(
        author_id=author_id,
        content=content,
        media_url=media_url,
        content_type=content_type,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_all_posts(db: Session) -> List[Post]:
    """
    Retrieves all posts from the database, ordered by creation date (newest first).
    """
    return db.query(Post).order_by(Post.created_at.desc()).all()