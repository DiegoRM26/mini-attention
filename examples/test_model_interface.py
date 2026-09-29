from mini_attention.vocabulary import Vocabulary
from mini_attention.attention import SelfAttention


vocab = Vocabulary()

attention = SelfAttention(
    vocabulary=vocab,
    embedding_dim=8,
    attention_dim=4
)

text = "Yo estoy en casa"

result = attention(text)

print("Type returned by SelfAttention:")
print(type(result))

print("\nShape:")
print(result.shape)

print("\nResult:")
print(result)