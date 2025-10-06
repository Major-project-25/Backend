# Backend/api/v1/routes_admin.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Path
from sqlalchemy.orm import Session
from uuid import UUID
import shutil
from typing import Optional

from DB.session import get_db
from schema.post_schema import PostResponse
from repositories import user_repo,post_repo
from model.user import User # This was missing in the previous code

router = APIRouter()

# Dependency to get the current user and check if they are an admin
# Note: The parameter name here is changed for clarity, but it's not strictly necessary.
def get_current_admin_user(user_id_from_path: UUID = Depends(lambda admin_id: admin_id), db: Session = Depends(get_db)) -> User:
    user = user_repo.get_user_by_id(db, user_id=user_id_from_path)
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
    # This dependency now correctly uses the admin_id from the path
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Creates a new post. Can be a text-only post, an image post, or a video post.
    - The admin_id in the path MUST match the current admin's ID.
    """
    # This check is now somewhat redundant due to the improved dependency, but it's good for an extra layer of validation.
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
        # Determine content type based on file's MIME type
        if "image" in file.content_type:
            content_type = "image"
        elif "video" in file.content_type:
            content_type = "video"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Please upload an image or video.",
            )

        # Save the file to a static directory
        file_path = f"Backend/static/uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # This URL would be what the frontend uses to fetch the media
        media_url = f"/static/uploads/{file.filename}"

    # Create the post in the database
    new_post = post_repo.create_post(
        db=db,
        author_id=current_admin.id,
        content=content,
        media_url=media_url,
        content_type=content_type,
    )

    return new_post