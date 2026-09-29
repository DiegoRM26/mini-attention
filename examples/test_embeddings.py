import numpy as np

from mini_attention.vocabulary import Vocabulary
from mini_attention.tokenizer import Tokenizer
from mini_attention.embeddings import Embedding


# -----------------------------------
# Vocabulary
# -----------------------------------

vocab = Vocabulary()


# -----------------------------------
# Tokenizer
# -----------------------------------

tokenizer = Tokenizer(vocab)


# -----------------------------------
# Embedding
# -----------------------------------

embedding = Embedding(
    vocab_size=len(vocab),
    embedding_dim=8
)


# -----------------------------------
# Frase
# -----------------------------------

text = "Yo no estoy en la oficina"


# -----------------------------------
# Token IDs
# -----------------------------------

token_ids = tokenizer.encode(text)


# -----------------------------------
# Obtener embeddings
# -----------------------------------

vectors = embedding(token_ids)


# -----------------------------------
# Mostrar resultados
# -----------------------------------

print("Text:")
print(text)

print("\nToken IDs:")
print(token_ids)

print("\nEmbedding shape:")
print(vectors.shape)

print("\nEmbeddings:")
print(vectors)