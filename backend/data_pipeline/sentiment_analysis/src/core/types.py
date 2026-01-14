from pydantic import BaseModel
from datetime import datetime

class UnprocessedComment(BaseModel):
    comment_id: str
    comment_body: str
    category: str
    detected_products: list[str]
    created_utc: datetime

class ProductSentiment(BaseModel):
    comment_id: str
    product_name: str
    category: str
    sentiment_score: float | None
    created_utc: datetime