import csv
import os
from datetime import datetime


def ExportCSV(
    comment_id: str,
    comment_body: str,
    subreddit: str,
    detected_products: list[str],
    timestamp: datetime,
    author: str,
    score: int,
    post_id: str,
) -> None:
    header = [
        "comment_id",
        "comment_body",
        "subreddit",
        "detected_products",
        "timestamp",
        "author",
        "score",
        "post_id",
    ]

    data = [
        comment_id,
        comment_body,
        subreddit,
        detected_products,
        timestamp,
        author,
        score,
        post_id,
    ]

    file_name = "testing3.csv"  # file name to export to
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
        script_dir,
        file_name,
    )
    file_exists = os.path.isfile(file_path)

    try:
        os.makedirs(
            script_dir,
            exist_ok=True,
        )
    except Exception as e:
        print(f"error with dir: {e}")
    else:
        with open(
            file_path,
            "a",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(
                file,
                quoting=csv.QUOTE_ALL,
            )
            if not file_exists:
                writer.writerow(header)
            writer.writerow(data)
