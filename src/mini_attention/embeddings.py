import numpy as np


class Embedding:

    def __init__(
        self,
        vocab_size,
        embedding_dim=8,
        seed=42
    ):
        """
        Crea una matriz de embeddings.

        Parameters
        ----------
        vocab_size : int
            Cantidad de tokens del vocabulario.

        embedding_dim : int
            Dimensiones de cada embedding.

        seed : int
            Semilla para reproducibilidad.
        """

        rng = np.random.default_rng(seed)

        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim

        self.weights = rng.normal(
            loc=0.0,
            scale=0.1,
            size=(vocab_size, embedding_dim)
        )

    def forward(self, token_ids):
        """
        Convierte IDs de tokens en embeddings.
        """

        return self.weights[token_ids]

    def __call__(self, token_ids):
        return self.forward(token_ids)


# -------------------------------------------------
# Compatibilidad con la versión anterior
# -------------------------------------------------

def create_embeddings(tokens):
    """
    Función temporal de compatibilidad.

    Esta función permite que el código antiguo
    continúe funcionando mientras migramos
    SelfAttention a la nueva arquitectura.
    """

    dimension = len(tokens)

    embeddings = np.eye(dimension)

    return embeddings


def create_qkv(embeddings):
    """
    Función temporal de compatibilidad.

    Genera Q, K y V a partir de los embeddings
    utilizando matrices identidad.

    Posteriormente eliminaremos esta función cuando
    SelfAttention utilice W_Q, W_K y W_V.
    """

    dimension = embeddings.shape[1]

    W_Q = np.eye(dimension)
    W_K = np.eye(dimension)
    W_V = np.eye(dimension)

    Q = embeddings @ W_Q
    K = embeddings @ W_K
    V = embeddings @ W_V

    return Q, K, V