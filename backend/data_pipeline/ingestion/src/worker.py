from src.utils.fetch_post import fetch_post_delayed
from src.utils.fetch_comments import fetch_comments
from src.utils.export_csv import ExportCSV
from src.preprocessing.relevant_fields import extract_relevant_fields, RedditComment
from src.preprocessing.url_remover import remove_url
from src.preprocessing.demojify import demojify
from src.preprocessing.is_valid_comment import is_valid_comment
from src.product_utils.gpu_detector import GPUDetector
from src.product_utils.gpu_normalization import GPUNameNormalizer
from src.core.reddit_client_instance import createRedditClient
from src.core.kafka_producer import KafkaClient
from src.preprocessing.check_english import detect_english
from src.core.logger import StructuredLogger
from praw.models import Submission, Comment
from praw import Reddit
import json
import prawcore


class Worker:
    def __init__(
        self,
        kafka_client=None,  # Dependency Injection Kafka Client for Testing
    ):
        self.logger = StructuredLogger(pod="idk")
        self.kafka_producer = kafka_client or KafkaClient(self.logger, bootstrap_server="localhost:9092")
        self.reddit_client: Reddit = createRedditClient()
        self.subreddits: list[str] = ["nvidia", "amd", "buildapc", "gamingpc", "pcbuild", "hardware"]
        self.gpu_detector = GPUDetector()
        self.gpu_normalizer = GPUNameNormalizer()

    def _fetch_all_posts(self) -> list[Submission]:
        """
        Fetch posts from all configured subreddits
        
        Returns:
           all_posts: list containing reddit post submission objects 
        """
        try:
            all_posts = []

            for subreddit in self.subreddits:
                posts: list[Submission] = list(
                    fetch_post_delayed(self.reddit_client, subreddit, self.logger)
                )
                if posts:
                    all_posts.extend(posts)
            
            return all_posts

        except prawcore.exceptions.ServerError:  # reddit api server error handling
            self.logger.error(
                event_type="Reddit Api",
                message="Server Error",
            )
            return []
        except Exception as e:
            self.logger.error(
                event_type="Reddit Api",
                message=f"Post Fetch Error: {e}",
            )
            return []

    def _process_comment(self, comment: Comment) -> RedditComment | None:
        """
        Extract, transform, and filter a comment

        Args:
            comment: single Praw reddit comment object

        Returns:
            RedditComment: Pydantic data object with relevant fields from the
                        comment like post_id, text, author, timestamp, upvotes
            None: none is returned if the comment is invalid
        """
        if not is_valid_comment(comment):
            return None
        
        # if the comment doesnt contain a gpu name or number we should skip it
        if not self.gpu_detector.contains_gpu(comment.body):
            return None
        
        gpus_in_comment: list[str] = self.gpu_detector.extract_gpus(comment.body)
        normalized_gpus: list[str] = self.gpu_normalizer.normalize_product_list(gpus_in_comment)

        # extracting only relevant parts of the comment api res
        extracted: RedditComment = extract_relevant_fields(comment, normalized_gpus)
        url_removed: str = remove_url(extracted.comment_body)
        demojified: str = demojify(url_removed)

        lang: str | None = detect_english(url_removed)
        if lang != "en":  # If the post is non-english skip it
            return None
        
        return RedditComment(
            comment_id=extracted.comment_id,
            comment_body=demojified,
            subreddit=extracted.subreddit,
            detected_products=extracted.detected_products,
            timestamp=extracted.timestamp,
            score=extracted.score,
            author=extracted.author,
            post_id=extracted.post_id
        )
    
    def _publish_to_kafka(self, processed_comment: RedditComment) -> None:
        """Publish a processed comment to kafka"""
        self.kafka_producer.send_message(
            topic="raw-data",
            message_body=json.loads(processed_comment.model_dump_json()),
            postID=processed_comment.comment_id,
        )
            
    def post_message(self):
        """Main orchestrator function: fetch, process, and publish comments"""
        all_posts = self._fetch_all_posts()
                    
        for post in all_posts:
            comments: list[Comment] = fetch_comments(post, self.logger)
            
            for comment in comments:
                processed_comment: RedditComment | None = self._process_comment(comment)
                if not processed_comment:
                    continue

                ExportCSV(
                    processed_comment.comment_id,
                    processed_comment.comment_body,
                    processed_comment.subreddit,
                    processed_comment.detected_products, 
                    processed_comment.timestamp, 
                    processed_comment.author, 
                    processed_comment.score, 
                    processed_comment.post_id
                )
                
                self._publish_to_kafka(processed_comment)

        print("flushing")
        self.kafka_producer.flush()


if __name__ == "__main__":
    for i in range(1):
        Worker().post_message()
