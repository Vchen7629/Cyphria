
# This function takes in the tfidf and category vocab list 
# and returns a list containing overlapping vocab

def constructor(tfidf_vocab: dict[str, int], category_vocab: list[str]) -> list[str]:
    idx_list = [
        tfidf_vocab[tok]
        for tok in category_vocab
        if tok in tfidf_vocab
    ]

    return idx_list