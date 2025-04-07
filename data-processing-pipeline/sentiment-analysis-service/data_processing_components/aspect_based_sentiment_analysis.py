from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import numpy as np
import torch, traceback, time

class Aspect_Based_Sentiment_Analysis:
    def __init__(self, tokenizer, model):
        self.tokenizer = tokenizer
        self.model = model

        self.id2label = {0: "negative", 1: "neutral", 2: "positive"}
    
    def SentimentAnalysis(self, pair):
        
        batch = []
        original_indices = []
        keywords = []
        for item in pair:
            indices = item[0]
            sentence = item[1]
            aspect = item[2]
            input_str = f"[CLS] {sentence} [SEP] {aspect} [SEP]"
            batch.append(input_str)
            original_indices.append(indices)
            keywords.append(aspect)

        try:
            start = time.time()
            tokens = self.tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**tokens)
            print(f"time to tokenize: {time.time() - start}")
            
            prob_batch = F.softmax(outputs.logits, dim=1)

            predicted_indices = torch.argmax(prob_batch, dim=1)

            predicted_indices_np = predicted_indices.cpu().numpy()

            predicted_labels = [self.id2label.get(idx, "unknown") for idx in predicted_indices_np]

            results = list(zip(original_indices, keywords, predicted_labels))
            
            print(f"time for sentiment analysis: {time.time() - start}")
            return results

        except Exception as e:
            print(f"Error processing: {e}")
            traceback.print_exc()
            return []