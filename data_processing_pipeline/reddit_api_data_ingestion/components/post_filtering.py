class PostFilter:
    def __init__(
        self,
    ):
        pass

    def postExists(
        self,
        apiRes,
    ):
        try:
            if "data" in apiRes and "children" in apiRes["data"]:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error checking post exists: {e}")

    def Extract_Relevant_Data(
        self,
        apiRes,
    ):
        try:
            if "data" in apiRes:
                post_data = apiRes["data"]
            else:
                post_data = apiRes

            extracted = {
                "title": post_data.get(
                    "title",
                    "",
                ),
                "body": post_data.get(
                    "selftext",
                    "",
                ),
                "subreddit": post_data.get(
                    "subreddit",
                    "",
                ),
                "upvotes": post_data.get(
                    "ups",
                    "",
                ),
                "downvotes": post_data.get(
                    "downs",
                    "",
                ),
                "post_id": post_data.get(
                    "id",
                    "",
                ),
                "created_utc": post_data.get(
                    "created_utc",
                    "",
                ),
            }

            # print(extracted)

            return extracted
        except Exception as e:
            print(e)
            return None


filter = PostFilter()
