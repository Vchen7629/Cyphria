from sentence_transformers import (  # type: ignore[import-not-found]
    SentenceTransformer,
)
import time
import os
import threading

_model_instance = None
_model_lock = threading.Lock()  # Use a lock for thread safety


def get_model():
    global _model_instance
    worker_pid = os.getpid()  # Get current Process ID

    # Fast path check
    if _model_instance is not None:
        return _model_instance

    # Acquire lock before modifying global state
    with _model_lock:
        # Double-check inside lock
        if _model_instance is not None:
            return _model_instance

        # --- Load the model ---
        print(f"--- [PID:{worker_pid}] Initializing SBERT model (loading now)... ---")
        start_time = time.time()
        try:
            device_to_use = "cpu"
            print(f"--- [PID:{worker_pid}] Loading model onto device: {device_to_use} ---")

            _model_instance = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2",
                device=device_to_use,
            )
            load_time = time.time() - start_time
            print(f"--- [PID:{worker_pid}] SBERT model initialized in: {load_time:.4f} seconds ---")
        except Exception as e:
            print(f"!!! [PID:{worker_pid}] ERROR Loading SBERT model: {e} !!!")
            raise e  # Re-raise

        return _model_instance
