import os


# function checks the reddit post for any stopwords
# using a txt file and removes them
def stop_words(rawData: str) -> str:
    # Fetching txt file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stopword_file_path = os.path.join(script_dir, "..", "configs", "stopwords.txt")
    with open(stopword_file_path, "r", encoding="utf-8") as f:
        stopword_instance = set(line.strip() for line in f if line.strip())

    tokenized_text = rawData.split()
    filtered_text = [word for word in tokenized_text if word.lower() not in stopword_instance]
    new_clean_text = " ".join(filtered_text)

    return new_clean_text
