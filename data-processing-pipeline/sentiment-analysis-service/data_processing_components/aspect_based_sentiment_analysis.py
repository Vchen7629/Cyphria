import torch.nn.functional as F
import torch, traceback, time, math

class Aspect_Based_Sentiment_Analysis:
    def __init__(self, tokenizer, model, device='cuda' if torch.cuda.is_available() else 'cpu', model_batch_size=32):
        self.tokenizer = tokenizer
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.model_batch_size = model_batch_size

        self.id2label = {0: "negative", 1: "neutral", 2: "positive"}
    
    def SentimentAnalysis(self, pair):
        if not pair:
            return []
        all_results = []
        num_batches = math.ceil(len(pair) / self.model_batch_size)
        try:
            for i in range(0, num_batches, self.model_batch_size):
                current_batch_pairs = pair[i : i + self.model_batch_size]

                if not current_batch_pairs: 
                    continue

                batch = []
                original_indices = []
                keywords = []

                for item in current_batch_pairs:
                    indices = item[0]
                    sentence = item[1]
                    aspect = item[2]
                    input_str = f"[CLS] {sentence} [SEP] {aspect} [SEP]"
                    batch.append(input_str)
                    original_indices.append(indices)
                    keywords.append(aspect)

                    start = time.time()

                tokens = self.tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.device)

                with torch.no_grad():
                    outputs = self.model(**tokens)
                print(f"time to tokenize: {time.time() - start}")
                    
                prob_batch = F.softmax(outputs.logits, dim=1)

                predicted_indices = torch.argmax(prob_batch, dim=1)

                predicted_indices_np = predicted_indices.cpu().numpy()

                predicted_labels = [self.id2label.get(idx, "unknown") for idx in predicted_indices_np]

                results = list(zip(original_indices, keywords, predicted_labels))
                all_results.extend(results)

                del tokens
                del outputs
                del prob_batch
                del predicted_indices
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                print(f"time for sentiment analysis: {time.time() - start}")
            return all_results
        except Exception as e:
            print(f"Error processing batch starting at index {i}: {e}")
            traceback.print_exc()
            return all_results