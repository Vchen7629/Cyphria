import torch.nn.functional as F
import torch
from typing import List


class Aspect_Based_Sentiment_Analysis:
    def __init__(  # type: ignore[no-untyped-def]
        self,
        tokenizer,
        model,
        device: str = "cpu",
        model_batch_size: int = 64,
    ) -> None:
        self.tokenizer = tokenizer
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.model_batch_size = model_batch_size

    def SentimentAnalysis(self, pairs: List[tuple[str, str, str]]) -> list[tuple[str, str, int]]:
        if not pairs:
            return []

        all_results = []
        num_pairs = len(pairs)

        for i in range(0, num_pairs, self.model_batch_size):
            current_batch = pairs[i : i + self.model_batch_size]

            post_ids = [x[0] for x in current_batch]
            sentences = [x[1] for x in current_batch]
            aspects = [x[2] for x in current_batch]

            tokens = self.tokenizer(
                sentences,
                aspects,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**tokens)

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
            batch_results = list(zip(post_ids, aspects, sentiment_scores))
            all_results.extend(batch_results)

        return all_results
