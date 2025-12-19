from pathlib import Path

stopword_file_path = Path(__file__).parent / "stopwords.txt"

with open(stopword_file_path, "r", encoding="utf-8") as f:
    stopword_instance = set(line.strip() for line in f if line.strip())


# Python Function To Remove StopWords
def stop_words(postBody: str) -> str:
    tokenized_text = postBody.split()
    filtered_text = [word for word in tokenized_text if word.lower() not in stopword_instance]
    new_clean_text = " ".join(filtered_text)

    return new_clean_text
