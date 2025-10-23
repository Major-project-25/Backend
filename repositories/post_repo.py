# Backend/repositories/post_repo.py

from sqlalchemy.orm import Session
from uuid import UUID
from model.post import Post
import os

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

def get_all_posts(db: Session) -> list[Post]:
    """ Fetches all posts, ordered by creation date (latest first). """
    return db.query(Post).order_by(Post.created_at.desc()).all()

# --- NEW FUNCTION TO DELETE A POST ---
def delete_post_by_id(db: Session, post_id: UUID) -> Post | None:
    """
    Finds a post by its ID and deletes it from the database.
    Also deletes the associated media file from the filesystem if it exists.
    """
    post_to_delete = db.query(Post).filter(Post.id == post_id).first()

    if not post_to_delete:
        return None # Post not found

    # Check if there is a media file associated with the post
    if post_to_delete.media_url:
        try:
            # Construct the absolute path to the file
            # Assumes the media_url is like "/static/uploads/filename.jpg"
            # We need to build the path relative to the project structure
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # The media_url starts with '/', so we strip it to correctly join paths
            file_path = os.path.join(BASE_DIR, post_to_delete.media_url.lstrip('/'))

            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted media file: {file_path}")
        except Exception as e:
            # Log the error but don't stop the process, as the DB record is more important
            print(f"Error deleting file {post_to_delete.media_url}: {e}")

    # Delete the post record from the database
    db.delete(post_to_delete)
    db.commit()
    
    return post_to_delete

