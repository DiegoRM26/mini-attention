import numpy as np
import matplotlib.pyplot as plt


def plot_attention(
    tokens,
    attention_weights,
    title="Attention Weights",
    ax=None
):
    """
    Visualiza una matriz de atención.

    Parameters
    ----------
    tokens : list[str]
        Tokens de la frase.

    attention_weights : np.ndarray
        Matriz de atención.

    title : str
        Título del gráfico.

    ax : matplotlib.axes.Axes, optional
        Eje sobre el cual dibujar.
        Si no se proporciona, se crea una nueva figura.
    """

    attention_weights = np.asarray(
        attention_weights
    )

    # ---------------------------------------------
    # Crear figura si no recibimos un eje
    # ---------------------------------------------

    if ax is None:

        fig, ax = plt.subplots(
            figsize=(8, 6)
        )

    else:

        fig = ax.figure

    # ---------------------------------------------
    # Heatmap
    # ---------------------------------------------

    image = ax.imshow(
        attention_weights,
        aspect="auto",
        vmin=0.0,
        vmax=1.0
    )

    # ---------------------------------------------
    # Eje X
    # ---------------------------------------------

    ax.set_xticks(
        np.arange(len(tokens))
    )

    ax.set_xticklabels(
        tokens,
        rotation=45,
        ha="right"
    )

    # ---------------------------------------------
    # Eje Y
    # ---------------------------------------------

    ax.set_yticks(
        np.arange(len(tokens))
    )

    ax.set_yticklabels(
        tokens
    )

    # ---------------------------------------------
    # Labels
    # ---------------------------------------------

    ax.set_xlabel(
        "Token atendido"
    )

    ax.set_ylabel(
        "Token actual"
    )

    ax.set_title(
        title
    )

    # ---------------------------------------------
    # Mostrar valores
    # ---------------------------------------------

    for i in range(
        attention_weights.shape[0]
    ):

        for j in range(
            attention_weights.shape[1]
        ):

            ax.text(
                j,
                i,
                f"{attention_weights[i, j]:.3f}",
                ha="center",
                va="center",
                fontsize=8
            )

    return fig, ax