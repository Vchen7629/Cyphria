from sentence_transformers import SentenceTransformer
import time

device_to_use = "cpu"

start = time.time()
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2", device=device_to_use
)
print(f"model loaded in {time.time() - start:.4f} seconds")
