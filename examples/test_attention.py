from mini_attention.vocabulary import Vocabulary
from mini_attention.attention import SelfAttention


# -----------------------------------
# Vocabulary
# -----------------------------------

vocab = Vocabulary()


# -----------------------------------
# Model
# -----------------------------------

model = SelfAttention(
    vocabulary=vocab,
    embedding_dim=8,
    attention_dim=4
)


# -----------------------------------
# Sentence
# -----------------------------------

text = "Yo estoy en casa"


# -----------------------------------
# Attention
# -----------------------------------

result = model(
    text,
    return_attention=True
)


# -----------------------------------
# Results
# -----------------------------------

print("Text:")
print(result["text"])

print("\nTokens:")
print(result["tokens"])

print("\nToken IDs:")
print(result["token_ids"])

print("\nEmbeddings shape:")
print(result["embeddings"].shape)

print("\nQ shape:")
print(result["Q"].shape)

print("\nK shape:")
print(result["K"].shape)

print("\nV shape:")
print(result["V"].shape)

print("\nScores:")
print(result["scores"])

print("\nAttention weights:")
print(result["attention_weights"])

print("\nOutput:")
print(result["output"])