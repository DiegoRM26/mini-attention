import matplotlib.pyplot as plt

from mini_attention.vocabulary import Vocabulary
from mini_attention.attention import SelfAttention
from mini_attention.visualization import plot_attention


# -------------------------------------------------
# 1. Crear vocabulario
# -------------------------------------------------

vocab = Vocabulary()


# -------------------------------------------------
# 2. Crear modelo
# -------------------------------------------------

model = SelfAttention(
    vocabulary=vocab,
    embedding_dim=8,
    attention_dim=4
)


# -------------------------------------------------
# 3. Frases para experimentar
# -------------------------------------------------

sentences = [
    "Yo estoy en casa",
    "Yo estoy en la oficina",
    "Yo no estoy en casa",
    "Yo no estoy en la oficina",
    "Yo salí de la casa",
    "Yo salí de la oficina",
]


# -------------------------------------------------
# 4. Crear figura para comparación
# -------------------------------------------------

fig, axes = plt.subplots(
    2,
    3,
    figsize=(16, 10)
)


# -------------------------------------------------
# 5. Procesar cada frase
# -------------------------------------------------

for sentence, ax in zip(
    sentences,
    axes.flatten()
):

    result = model(
        sentence,
        return_attention=True
    )

    tokens = result["tokens"]

    attention_weights = result[
        "attention_weights"
    ]

    # ---------------------------------------------
    # Información en consola
    # ---------------------------------------------

    print("\n" + "=" * 60)

    print("Sentence:")
    print(sentence)

    print("\nTokens:")
    print(tokens)

    print("\nAttention weights:")

    print(attention_weights)

    print("\nRow sums:")

    print(
        attention_weights.sum(axis=1)
    )

    # ---------------------------------------------
    # Dibujar heatmap
    # ---------------------------------------------

    plot_attention(
        tokens=tokens,
        attention_weights=attention_weights,
        title=sentence,
        ax=ax
    )


# -------------------------------------------------
# 6. Ajustar distribución
# -------------------------------------------------

plt.tight_layout()


# -------------------------------------------------
# 7. Mostrar todas las gráficas
# -------------------------------------------------

plt.show()