from datetime import datetime
from pydantic import BaseModel

class top_comment(BaseModel):
    """Single top comment containing comment text, link, and score"""
    comment_text: str
    reddit_link: str
    score: int
    created_utc: datetime
