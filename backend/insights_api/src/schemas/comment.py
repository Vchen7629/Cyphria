from pydantic import BaseModel

class top_comment(BaseModel):
    """Single top comment containing comment text, link, and score"""
    comment_text: str
    link: str
    score: int
