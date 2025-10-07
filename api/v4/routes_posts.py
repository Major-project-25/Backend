# Backend/api/v1/routes_posts.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from DB.session import get_db
from schema.post_schema import PostResponse
from repositories import post_repo

router = APIRouter()

@router.get("/", response_model=List[PostResponse])
def get_all_posts_for_users(db: Session = Depends(get_db)):
    """
    Fetches all posts created by the admin, sorted with the latest posts first.
    This endpoint is for regular users to view the content feed.
    """
    posts = post_repo.get_all_posts(db)
    return posts
