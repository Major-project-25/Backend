# Backend/api/v4/routes_posts.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID
from typing import List

from DB.session import get_db
from schema.post_schema import PostResponse, ReactionCreate # Import ReactionCreate
from model.post import Post # Import Post model
from repositories import post_repo, post_reaction_repo # Import the new repo

router = APIRouter()

@router.get("/{user_id}", response_model=List[PostResponse])
def get_all_posts(user_id: UUID, db: Session = Depends(get_db)):
    """
    Fetches all posts and includes reaction counts and the current user's reaction.
    """
    # This raw SQL query is more efficient for joining and checking the user's reaction
    query = text("""
        SELECT 
            p.*, 
            pr.reaction_type as user_reaction
        FROM posts p
        LEFT JOIN post_reactions pr ON p.id = pr.post_id AND pr.user_id = :user_id
        ORDER BY p.created_at DESC
    """)
    
    results = db.execute(query, {"user_id": user_id}).fetchall()
    
    # The results are raw rows, we need to map them to Pydantic models
    posts_with_reactions = []
    for row in results:
        post_data = dict(row._mapping) # Convert row to dictionary
        posts_with_reactions.append(PostResponse(**post_data))
        
    return posts_with_reactions


# --- NEW ENDPOINT FOR REACTIONS ---
@router.post("/{post_id}/react/{user_id}", response_model=PostResponse)
def react_to_a_post(
    post_id: UUID,
    user_id: UUID,
    reaction: ReactionCreate,
    db: Session = Depends(get_db)):
    """
    Allows a user to 'like', 'dislike', or remove their reaction ('none') from a post.
    """
    updated_post = post_reaction_repo.react_to_post(
        db=db,
        user_id=user_id,
        post_id=post_id,
        new_reaction_type=reaction.reaction_type
    )

    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )
    
    # We need to fetch the user's latest reaction state to return it
    final_post_data = get_all_posts(user_id=user_id, db=db)
    for post in final_post_data:
        if post.id == post_id:
            return post
    
    # Fallback in case the post is not found in the list (should not happen)
    return updated_post
