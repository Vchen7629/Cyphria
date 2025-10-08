import praw
from datetime import datetime
from pydantic import BaseModel
from ..middleware.logger import StructuredLogger


# This pydantic class implements a type interface
# for processed reddit posts
class RedditPost(BaseModel):
    body: str  # full body (title + selftext)
    subreddit: str
    timestamp: datetime
    id: str

# Python Function to extract relevant data from reddit
# posts before sending to the kafka producer
def process_post(
    apiRes: praw.models.Submission,
    logger: StructuredLogger
) -> RedditPost:
    title = apiRes.title or ""
    selftext = apiRes.selftext or ""
    fullBody = title + " " + selftext

    if fullBody == " ":
        logger.error(
            event_type="data_ingestion",
            message="Post Missing Body Text",
            post_id=apiRes.id,
        )
    
    return RedditPost(
        body=fullBody,
        subreddit=apiRes.subreddit.display_name,
        timestamp=apiRes.created_utc,
        id=apiRes.id,
    )
