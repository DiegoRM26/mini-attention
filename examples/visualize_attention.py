from mini_attention.vocabulary import Vocabulary
from mini_attention.attention import SelfAttention
from mini_attention.visualization import plot_attention


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
# Mostrar información
# -----------------------------------

print("Tokens:")
print(result["tokens"])

print("\nAttention weights:")
print(result["attention_weights"])


# -----------------------------------
# Visualización
# -----------------------------------

plot_attention(
    tokens=result["tokens"],
    attention_weights=result["attention_weights"],
    title=f"Self-Attention: {text}"
)

# Mostrar gráfico
import matplotlib.pyplot as plt

plt.show()