from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

from typing import Optional, Tuple

# yangheng/deberta-v3-base-absa-v1.1


def sentiment_analysis_model(
    model_name: str,
) -> Optional[Tuple[AutoTokenizer, AutoModelForSequenceClassification]]:
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        return tokenizer, model
    except Exception as e:
        print(f"Error initializing models: {e}")
        raise RuntimeError(f"Failed to load model {model_name}") from e
