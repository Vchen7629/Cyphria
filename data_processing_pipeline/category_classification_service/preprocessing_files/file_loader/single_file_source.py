import os 

def vocabLoader(folder_name: str, file_name: str) -> list[str]:
    basedir = os.path.dirname(os.path.abspath(__file__))
    txt_path = os.path.join(basedir, "..", "..", folder_name, file_name)

    with open(txt_path, "r") as f:
        return [line.strip() for line in f]