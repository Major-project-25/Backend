# Backend/api/v4/routes_admin.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID
import shutil
from typing import Optional

from DB.session import get_db
from schema.post_schema import PostResponse
from repositories import user_repo, post_repo
from model.user import User
import os # Import os for path operations

router = APIRouter()

# Dependency to get the current user and check if they are an admin
def get_current_admin_user(user_id: UUID, db: Session = Depends(get_db)) -> User:
    user = user_repo.get_user_by_id(db, user_id=user_id)
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action.",
        )
    return user

@router.post("/{admin_id}/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    admin_id: UUID,
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Creates a new post. Can be a text-only post, an image post, or a video post.
    """
    if admin_id != current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin ID in path does not match authenticated admin.",
        )
        
    if not content and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A post must have either text content or a file.",
        )

    media_url = None
    content_type = "text"

    if file:
        if "image" in file.content_type:
            content_type = "image"
        elif "video" in file.content_type:
            content_type = "video"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Please upload an image or video.",
            )

        # Correctly get the base directory and save the file
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads")
        file_path = os.path.join(UPLOADS_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        media_url = f"/static/uploads/{file.filename}"

    new_post = post_repo.create_post(
        db=db,
        author_id=current_admin.id,
        content=content,
        media_url=media_url,
        content_type=content_type,
    )

    return new_post

# --- NEW ENDPOINT TO DELETE A POST ---
@router.delete("/{admin_id}/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_a_post(
    admin_id: UUID,
    post_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Deletes a specific post by its ID. Only accessible by an admin.
    """
    if admin_id != current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin ID in path does not match authenticated admin.",
        )

    deleted_post = post_repo.delete_post_by_id(db, post_id=post_id)

    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found."
        )
    
    # A 204 response does not have a body, so we return nothing.
    return
