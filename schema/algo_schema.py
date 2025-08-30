# schema/algo_schema.py

from pydantic import BaseModel
from typing import List
from uuid import UUID

class MatchResponse(BaseModel):
    """
    Defines the response model for the matching endpoint,
    returning a list of user UUIDs.
    """
    matches: List[UUID]