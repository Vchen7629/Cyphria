from shared_core.logger import StructuredLogger
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from typing import Tuple


# yangheng/deberta-v3-base-absa-v1.1
def sentiment_analysis_model(
    model_name: str,
) -> Tuple[AutoTokenizer, AutoModelForSequenceClassification]:
    """
    Loads the ABSA model

    Args:
        model_name: the absa model we are loading

    Returns:
        the tokenizer and model required for doing absa inference

    Raises:
        Runtime error if an error occurs
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        return tokenizer, model
    except Exception as e:
        StructuredLogger(pod="sentiment_analysis").error(
            event_type="sentiment_analysis startup", message=f"Error initializing models: {str(e)}"
        )

        raise RuntimeError(f"Failed to load model {model_name}") from e
