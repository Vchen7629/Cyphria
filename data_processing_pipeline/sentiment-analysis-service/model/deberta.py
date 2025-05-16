from transformers import AutoTokenizer, AutoModelForSequenceClassification

class DebertaModel:
    def __init__(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("yangheng/deberta-v3-base-absa-v1.1")
            self.model = AutoModelForSequenceClassification.from_pretrained("yangheng/deberta-v3-base-absa-v1.1")
        except Exception as e:
            print(f"Error initializing models: {e}")

deberta = DebertaModel()