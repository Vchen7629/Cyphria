from pydantic import BaseModel
from datetime import datetime

# Pydantic class for reddit comments
class RedditComment(BaseModel):
    comment_id: str
    comment_body: str
    subreddit: str
    detected_products: list[str]
    timestamp: datetime
    score: int
    author: str
    post_id: str