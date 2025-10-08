import re, os


class RedditPosts:
    def __init__(
        self,
    ):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        stopword_file_path = os.path.join(
            script_dir,
            "..",
            "datasets",
            "stopwords.txt",
        )

        with open(
            stopword_file_path,
            "r",
            encoding="utf-8",
        ) as f:
            self.stopword_instance = set(line.strip() for line in f if line.strip())

    # This private function checks the reddit post for url links and
    # removes them
    def _remove_url(
        self,
        rawdata: str,
    ) -> str:
        url_pattern = re.compile(r"https?://\S+|www\.\S+")
        result = url_pattern.sub(
            "",
            rawdata,
        )

        return result

    # This private function checks the reddit post for any stopwords
    # using a txt file and removes them
    def _stop_words(
        self,
        rawData: str,
    ) -> str:
        tokenized_text = rawData.split()
        filtered_text = [
            word for word in tokenized_text if word.lower() not in self.stopword_instance
        ]
        new_clean_text = " ".join(filtered_text)

        return new_clean_text

    def removeNoise(
        self,
        rawtext: str,
    ):
        filter_url = self._remove_url(rawtext)
        filter_stopwords = self._stop_words(filter_url)

        return filter_stopwords
