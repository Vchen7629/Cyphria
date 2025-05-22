import os
import pandas as pd

def replaceText(rawtext):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    programming_tools_data_txt_path = os.path.join(base_dir, '..', 'datasets', 'programming_tools.txt')
    programming_tools_df = pd.read_csv(programming_tools_data_txt_path, header=None)
    programming_tools = set(w.lower() for w in programming_tools_df[0].str.strip())

    tokenized_text = rawtext.split()
    dataset = programming_tools
    new_sentence = []

    for word in tokenized_text:
        clean_word = word.strip('.,!?') 
        if clean_word.lower() in dataset:
            new_sentence.append('[programmingtool]')
        else:
            new_sentence.append(word)
                
    return ' '.join(new_sentence)