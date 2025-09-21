import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.insert(0, project_root)

from data_processing_pipeline.category_classification_service import get_reddit_posts


class TestExtractRelevantData:
    def setup_method(self):
        self.mock_api_res_has_data_field = {
            "kind": "t3",
            "data": {
                "subreddit": "test subreddit",
                "selftext": "This is a test post body",
                "title": "This is a test post title",
                "some random field": "This is a random field",
                "ups": 39,
                "downs": 21,
                "created_utc": 1747232581,
            },
        }

        self.mock_api_res = {
            "subreddit": "test subreddit",
            "selftext": "This is a test post body",
            "title": "This is a test post title",
            "some random field": "This is a random field",
            "ups": 39,
            "downs": 21,
            "created_utc": 1747232581,
        }

        self.mock_api_res_no_title = {
            "subreddit": "test subreddit",
            "selftext": "This is a test post body",
            "some random field": "This is a random field",
            "ups": 39,
            "downs": 21,
            "created_utc": 1747232581,
        }

        self.mock_api_res_no_body = {
            "subreddit": "test subreddit",
            "title": "This is a test post title",
            "some random field": "This is a random field",
            "ups": 39,
            "downs": 21,
            "created_utc": 1747232581,
        }

        self.mock_api_res_no_subreddit = {
            "selftext": "This is a test post body",
            "title": "This is a test post title",
            "some random field": "This is a random field",
            "ups": 39,
            "downs": 21,
            "created_utc": 1747232581,
        }

        self.mock_api_res_no_upvotes = {
            "subreddit": "test subreddit",
            "selftext": "This is a test post body",
            "title": "This is a test post title",
            "some random field": "This is a random field",
            "downs": 21,
            "created_utc": 1747232581,
        }

        self.mock_api_res_no_downvotes = {
            "subreddit": "test subreddit",
            "selftext": "This is a test post body",
            "title": "This is a test post title",
            "some random field": "This is a random field",
            "ups": 39,
            "created_utc": 1747232581,
        }

        self.mock_api_res_no_timestamp = {
            "subreddit": "test subreddit",
            "selftext": "This is a test post body",
            "title": "This is a test post title",
            "some random field": "This is a random field",
            "ups": 39,
            "downs": 21,
        }

    def test_appends_title_body(self):
        has_data_field = self.mock_api_res_has_data_field
        no_data_field = self.mock_api_res
        result_with_data_field = get_reddit_posts.extractData(has_data_field)
        result_no_data_field = get_reddit_posts.extractData(no_data_field)

        assert (
            result_with_data_field[0]
            == "This is a test post title This is a test post body"
        )
        assert (
            result_no_data_field[0]
            == "This is a test post title This is a test post body"
        )

    def test_works_with_no_title(self):
        no_title_res = self.mock_api_res_no_title
        result = get_reddit_posts.extractData(no_title_res)

        assert result[0] == " This is a test post body"

    def test_works_with_no_body(self):
        no_body_res = self.mock_api_res_no_body
        result = get_reddit_posts.extractData(no_body_res)

        assert result[0] == "This is a test post title "

    def test_returns_all_fields(self):
        api_res = self.mock_api_res
        result = get_reddit_posts.extractData(api_res)

        assert result[0] == "This is a test post title This is a test post body"
        assert result[1] == "test subreddit"
        assert result[2] == 39
        assert result[3] == 21
        assert result[4] == 1747232581

    def test_works_with_no_subreddit(self):
        api_res = self.mock_api_res_no_subreddit
        result = get_reddit_posts.extractData(api_res)
        expected = (
            "This is a test post title This is a test post body",
            "",
            39,
            21,
            1747232581,
        )

        assert result == expected

    def test_works_with_no_upvotes(self):
        api_res = self.mock_api_res_no_upvotes
        result = get_reddit_posts.extractData(api_res)
        expected = (
            "This is a test post title This is a test post body",
            "test subreddit",
            "",
            21,
            1747232581,
        )

        assert result == expected

    def test_works_with_no_downvotes(self):
        api_res = self.mock_api_res_no_downvotes
        result = get_reddit_posts.extractData(api_res)
        expected = (
            "This is a test post title This is a test post body",
            "test subreddit",
            39,
            "",
            1747232581,
        )

        assert result == expected

    def test_works_with_no_utc(self):
        api_res = self.mock_api_res_no_timestamp
        result = get_reddit_posts.extractData(api_res)
        expected = (
            "This is a test post title This is a test post body",
            "test subreddit",
            39,
            21,
            "",
        )

        assert result == expected
