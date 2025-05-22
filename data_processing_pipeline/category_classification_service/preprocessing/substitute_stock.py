import os
import pandas as pd

def replaceText(rawtext):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stock_data_txt_path = os.path.join(base_dir, '..', 'datasets', 'stock_names.txt')
    stock_names_df = pd.read_csv(stock_data_txt_path, header=None)
    stock_names = set(stock_names_df[0].str.strip())

    tokenized_text = rawtext.split()
    dataset = stock_names
    new_sentence = []

    for word in tokenized_text:
        if word in dataset or (word.startswith('$') and word[1:] in dataset):
            new_sentence.append('[stock]')
        else:
            new_sentence.append(word)

    return ' '.join(new_sentence)