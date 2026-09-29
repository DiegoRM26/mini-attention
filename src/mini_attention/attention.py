import numpy as np


class SelfAttention:
    """
    Implementación sencilla de Scaled Dot-Product Self-Attention.

    En esta etapa:
    - Embeddings permanecen congelados.
    - W_Q, W_K y W_V son entrenables.
    - Se guardan los valores necesarios para posteriormente
      implementar Backpropagation.
    """

    def __init__(
        self,
        vocabulary,
        embedding_dim=8,
        attention_dim=4,
        seed=42
    ):
        self.vocabulary = vocabulary
        self.embedding_dim = embedding_dim
        self.attention_dim = attention_dim

        # Embeddings
        rng = np.random.default_rng(seed)

        self.embeddings = rng.normal(
            0,
            0.1,
            size=(vocabulary.size, embedding_dim)
        )

        # Parámetros de Attention
        self.W_Q = rng.normal(
            0,
            0.1,
            size=(embedding_dim, attention_dim)
        )

        self.W_K = rng.normal(
            0,
            0.1,
            size=(embedding_dim, attention_dim)
        )

        self.W_V = rng.normal(
            0,
            0.1,
            size=(embedding_dim, attention_dim)
        )

        # Valores guardados durante forward
        self.attention_weights = None
        self.last_input = None
        self.last_Q = None
        self.last_K = None
        self.last_V = None
        self.last_scores = None
        self.last_output = None

    @property
    def tokenizer(self):
        """Retorna el tokenizer del vocabulario para acceso directo."""
        return self.vocabulary.tokenizer

    def softmax(self, x):
        """
        Softmax numéricamente estable.
        """

        x = x - np.max(
            x,
            axis=-1,
            keepdims=True
        )

        exp_x = np.exp(x)

        return exp_x / np.sum(
            exp_x,
            axis=-1,
            keepdims=True
        )

    def forward(self, text, return_attention=False):
        """
        Ejecuta Self-Attention.

        Parameters
        ----------
        text : str
            Texto a procesar
        return_attention : bool, default=False
            Si True, retorna diccionario con detalles intermedios.
            Si False, retorna solo output (ndarray)

        Returns
        -------
        output : np.ndarray or dict
            Si return_attention=False: (n_tokens, attention_dim)
            Si return_attention=True: dict con keys:
                - text, tokens, token_ids
                - embeddings, Q, K, V, scores
                - attention_weights, output
        """

        # --------------------------------------------------
        # 1. Tokenización
        # --------------------------------------------------

        token_ids = self.vocabulary.tokenizer.tokenize_to_ids(text)
        tokens = self.vocabulary.tokenizer.tokenize(text)

        # --------------------------------------------------
        # 2. Embeddings
        # --------------------------------------------------

        X = self.embeddings[token_ids]

        # Guardamos entrada
        self.last_input = X

        # --------------------------------------------------
        # 3. Q, K, V
        # --------------------------------------------------

        Q = X @ self.W_Q
        K = X @ self.W_K
        V = X @ self.W_V

        self.last_Q = Q
        self.last_K = K
        self.last_V = V

        # --------------------------------------------------
        # 4. Scaled Dot-Product Attention
        # --------------------------------------------------

        scores = (
            Q @ K.T
        ) / np.sqrt(self.attention_dim)

        self.last_scores = scores

        # --------------------------------------------------
        # 5. Softmax
        # --------------------------------------------------

        attention_weights = self.softmax(scores)

        self.attention_weights = attention_weights

        # --------------------------------------------------
        # 6. Weighted sum
        # --------------------------------------------------

        output = attention_weights @ V

        self.last_output = output

        # Retornar según parámetro
        if return_attention:
            return {
                "text": text,
                "tokens": tokens,
                "token_ids": list(token_ids),
                "embeddings": X,
                "Q": Q,
                "K": K,
                "V": V,
                "scores": scores,
                "attention_weights": attention_weights,
                "output": output
            }
        else:
            return output

    def __call__(self, text, return_attention=False):
        """
        Permite utilizar:

            attention(text, return_attention=True)

        en lugar de:

            attention.forward(text, return_attention=True)
        """

        return self.forward(text, return_attention=return_attention)