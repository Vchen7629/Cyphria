import torch.nn.functional as F
import torch
from typing import List
from concurrent.futures import ThreadPoolExecutor
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification

class Aspect_Based_Sentiment_Analysis:
    def __init__(
        self,
        tokenizer: AutoTokenizer,
        model: AutoModelForSequenceClassification,
        executor: ThreadPoolExecutor,
        device: str = "cpu",
        model_batch_size: int = 64,
    ) -> None:
        self.tokenizer = tokenizer
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.model_batch_size = model_batch_size
        self.executor = executor

    def _inference(self, sentences, aspects, tokenizer, model, device): # type: ignore[no-untyped-def]
        tokens = tokenizer(
            sentences,
            aspects,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(device)

        with torch.no_grad():
            outputs = model(**tokens)

        return outputs

    def SentimentAnalysis(self, product_pairs: List[tuple[str, str]]) -> list[tuple[str, int]]:
        """
        Public method for running ABSA sentiment analysis. Does sentiment analysis of the sentiments
        of the comment torwards a product in the comment
        
        Args:
            product_pairs: a list of product pair tuples (comment_text, product)

        Returns:
            a list of tuples of the sentiment score torwards the product in the comment
        """
        if not product_pairs:
            return []

        all_results = []
        num_pairs = len(product_pairs)

        for i in range(0, num_pairs, self.model_batch_size):
            current_batch = product_pairs[i : i + self.model_batch_size]

            sentences = [x[0] for x in current_batch]
            aspects = [x[1] for x in current_batch]

            future = self.executor.submit(
                self._inference,
                sentences,
                aspects,
                self.tokenizer,
                self.model,
                self.device
            )

            try:
                outputs = future.result(timeout=3)
            except TimeoutError:
                print(f"ABSA inference timed out for batch starting at index {i} — skipping this batch")
                continue 

            # Compute probabilities
            prob_batch = F.softmax(outputs.logits, dim=1)

            # Unpack into negative, neutral, positive
            p_neg = prob_batch[:, 0]
            p_neu = prob_batch[:, 1]
            p_pos = prob_batch[:, 2]

            # Weighted average score in range [-1, 1]
            sentiment_score = (-1 * p_neg) + (0 * p_neu) + (1 * p_pos)

            # Convert to rounded list
            sentiment_scores = [round(s.item(), 3) for s in sentiment_score]

            # outputs: [('abc123', 'controller', '0.5'), ('abc123', 'graphics', '-0.1')]
            batch_results = list(zip(aspects, sentiment_scores))
            all_results.extend(batch_results)

        return all_results
