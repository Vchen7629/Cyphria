from sentence_transformers import SentenceTransformer
from ..middleware.logger import StructuredLogger


def get_model(device: str, logger: StructuredLogger):  # type: ignore
    try:
        model_instance = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device=device,
        )

        logger.info(event_type="model_loading", message="Successfully loading SBert Model!")

        return model_instance
    except Exception as e:
        logger.error(event_type="model_loading", message=f"Error loading Sbert Model: {e}")

        return None
