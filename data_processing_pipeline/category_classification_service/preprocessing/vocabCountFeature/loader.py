import os, sys, importlib
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import importlib

class VocabCoordinator:
    def __init__(self, folder_name: str) -> None:
        self.folder_name = folder_name
        self.basedir = os.path.dirname(os.path.abspath(__file__))

    def _file_vars(self) -> list[tuple[str, str, str, bool, list[str]]]:
        return [
            # category name or key, file type, subfolder name, is_class, txt file names
            ("animals", "multi_file_source", "animal", True, ["species.txt", "terms.txt"]),
            ("anime", "multi_file_source", "anime", True, ["terms.txt", "types.txt"]),
            ("art", "multi_file_source", "art", True, ["terms.txt", "companies.txt", "styles.txt"]),
            ("jobs", "multi_file_source", "job", True, ["terms.txt", "websites.txt"]),
            ("law", "single_file_source", "", False, "law_terms.txt"),
            ("food", "multi_file_source", "food", True, ["appliances.txt", "drink.txt", "item.txt", "utensils.txt", "terms.txt"]),
            ("health", "multi_file_source", "health", True, ["condition.txt", "doctor_specialty.txt", "drug_names.txt", "body_parts.txt", "terms.txt"]),
            ("gaming", "multi_file_source", "gaming", True, ["terms.txt", "type.txt", "consoles.txt", "companies.txt"]),
            ("history", "multi_file_source", "history", True, ["civilizations.txt", "historical_period.txt", "terms.txt"]),
            ("housing", "multi_file_source", "housing", True, ["terms.txt", "types.txt"]),
            ("business", "multi_file_source", "business", True, ["models.txt", "terms.txt", "type.txt"]),
            ("gardening", "multi_file_source", "gardening", True, ["plants.txt", "terms.txt", "tools.txt"]),
            ("literature", "multi_file_source", "literature", True, ["genre.txt", "terms.txt", "type.txt"]),
            ("investments", "multi_file_source", "investing", True, ["brokers.txt", "stock_tickers.txt", "terms.txt"]),
            ("money", "multi_file_source", "money", True, ["banks.txt", "terms.txt"]),
            ("movies", "multi_file_source", "movies", True, ["companies.txt", "terms.txt", "types.txt"]),
            ("music", "multi_file_source", "music", True, ["instrument.txt", "style.txt", "terms.txt"]),
            ("photography", "multi_file_source", "photography", True, ["companies.txt", "terms.txt", "apps.txt"]),
            ("politics", "multi_file_source", "politics", True, ["types.txt", "terms.txt"]),
            ("programming", "multi_file_source", "programming", True, ["terms.txt", "os.txt", "tools.txt"]),
            ("travel", "multi_file_source", "travel", True, ["airlines.txt", "companies.txt", "terms.txt"]),
            ("relationships", "multi_file_source", "relationship", True, ["terms.txt", "dating_apps.txt"]),
            ("religion", "multi_file_source", "religion", True, ["religion.txt", "terms.txt"]),
            ("science", "multi_file_source", "science", True, ["terms.txt", "astronomy.txt", "geology.txt", "physics.txt"]),
            ("sports", "multi_file_source", "sports", True, ["leagues.txt", "teams.txt", "terms.txt", "tournaments.txt"]),
            ("technology", "multi_file_source", "technology", True, ["companies.txt", "cpu_names.txt", "gpu_names.txt", "motherboard_names.txt", "terms.txt"]),
            ("tv_shows", "multi_file_source", "tv_shows", True, ["companies.txt", "terms.txt"]),
            ("collecting", "multi_file_source", "collecting", True, ["terms.txt", "types.txt", "companies.txt"]),
            ("vehicles", "multi_file_source", "vehicle", True, ["name.txt", "terms.txt", "type.txt", "companies.txt"]),
            ("education", "multi_file_source", "education", True, ["courses.txt", "terms.txt", "universities.txt"]),
            ("fashion", "multi_file_source", "fashion", True, ["terms.txt", "types.txt"]),
        ]

    def vocabDictBuilder(self) -> dict[str, list[str]]:
        file_vars = self._file_vars()
        vocabDict = {}

        for key, py_file, subfolder_name, is_class, txt_file_names in file_vars:
            module = importlib.import_module(f"file_loader.{py_file}")

            if is_class:
                loader = module.VocabLoader(self.folder_name, subfolder_name)
                vocabDict[key] = loader.combineVocab(txt_file_names)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                txt_path = os.path.join(base_dir, "..", "..", self.folder_name, txt_file_names)
                with open(txt_path, "r", encoding="utf-8") as f:
                    vocabDict[key] = [line.strip() for line in f if line.strip()]
            
        return vocabDict
        
