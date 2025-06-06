import os

class VocabLoader:
    def __init__(self, folder_name: str, subfolder_name: str):
        self.folder_name = folder_name
        self.subfolder_name = subfolder_name
        self.basedir = os.path.dirname(os.path.abspath(__file__))

    def _load_data(self, filename: str) -> list[str]:
        txt_path = os.path.join(self.basedir, "..", "..", self.folder_name, self.subfolder_name, filename)

        with open(txt_path, "r") as f:
            return [line.strip() for line in f]
    
    def combineVocab(self, files: list[str]) -> list[str]:
        combined_arr = []

        for file in files:
            vocab = self._load_data(file)
            combined_arr.extend(vocab)

        return combined_arr
    