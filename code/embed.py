from sentence_transformers import SentenceTransformer
import pandas as pd
import torch
if not hasattr(torch, 'get_default_device'):
    def get_default_device():
        return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.get_default_device = get_default_device

print("Initiated Embedding process.......")

# Load chunks
df = pd.read_csv('voxcinemas_chunks.csv')

# Load SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Move model to the appropriate device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

# Batch encode for efficiency
chunks = df['chunk'].astype(str).tolist()
embeddings = model.encode(chunks, normalize_embeddings=True, show_progress_bar=True)

# Save embeddings as list
df['embedding'] = embeddings.tolist()

# Save the resulting DataFrame
df.to_csv("voxcinemas_with_embeddings.csv", index=False)
print("Embeddings added and saved ✅")
