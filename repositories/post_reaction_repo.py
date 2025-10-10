# Backend/repositories/post_reaction_repo.py

from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from model.post import Post
from model.post_reaction import PostReaction

def react_to_post(db: Session, user_id: UUID, post_id: UUID, new_reaction_type: str):
    """
    Manages user reactions to a post and updates the like/dislike counts.
    This is the most complex part of the logic.
    """
    # Find the post that is being reacted to
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None # Post not found

    # Check if the user has an existing reaction to this post
    existing_reaction = db.query(PostReaction).filter(
        and_(PostReaction.post_id == post_id, PostReaction.user_id == user_id)
    ).first()

    # --- LOGIC TO UPDATE COUNTS ---
    if existing_reaction:
        # User is changing or removing their reaction
        old_reaction_type = existing_reaction.reaction_type

        # Decrement the old counter if the reaction is changing
        if old_reaction_type == 'like':
            post.likes -= 1
        elif old_reaction_type == 'dislike':
            post.dislikes -= 1
        
        if new_reaction_type == 'none':
            # User is removing their reaction
            db.delete(existing_reaction)
        else:
            # User is changing their reaction
            existing_reaction.reaction_type = new_reaction_type
            # Increment the new counter
            if new_reaction_type == 'like':
                post.likes += 1
            elif new_reaction_type == 'dislike':
                post.dislikes += 1
    else:
        # User is reacting for the first time
        if new_reaction_type != 'none':
            new_reaction = PostReaction(
                post_id=post_id,
                user_id=user_id,
                reaction_type=new_reaction_type
            )
            db.add(new_reaction)
            # Increment the new counter
            if new_reaction_type == 'like':
                post.likes += 1
            elif new_reaction_type == 'dislike':
                post.dislikes += 1

    db.commit()
    db.refresh(post)
    return post
