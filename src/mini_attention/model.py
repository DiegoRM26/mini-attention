import numpy as np

from .attention import SelfAttention
from .classifier import Classifier


class AttentionClassifier:
    """
    Modelo completo:

    Texto
        ↓
    Tokenizer
        ↓
    Embeddings
        ↓
    Self-Attention
        ↓
    Mean Pooling
        ↓
    Classifier
        ↓
    Softmax
    """

    def __init__(
        self,
        vocabulary,
        embedding_dim=8,
        attention_dim=4,
        num_classes=2
    ):

        self.attention = SelfAttention(
            vocabulary=vocabulary,
            embedding_dim=embedding_dim,
            attention_dim=attention_dim
        )

        self.classifier = Classifier(
            input_dim=attention_dim,
            num_classes=num_classes
        )

    def forward(
        self,
        text,
        return_attention=False
    ):
        """
        Ejecuta el modelo completo.
        """

        # -----------------------------------------
        # Self-Attention
        # -----------------------------------------

        attention_output = self.attention(text)

        # -----------------------------------------
        # Mean Pooling
        # -----------------------------------------

        sentence_vector = np.mean(
            attention_output,
            axis=0
        )

        # -----------------------------------------
        # Classifier
        # -----------------------------------------

        probabilities = (
            self.classifier.predict_proba(
                sentence_vector
            )
        )

        prediction = self.classifier.predict(
            sentence_vector
        )

        # -----------------------------------------
        # Tokens
        # -----------------------------------------

        tokens = self.attention.tokenizer.tokenize(
            text
        )

        result = {
            "text": text,
            "tokens": tokens,
            "sentence_vector": sentence_vector,
            "probabilities": probabilities,
            "prediction": prediction
        }

        # -----------------------------------------
        # Attention information
        # -----------------------------------------

        if return_attention:

            result["attention_output"] = (
                attention_output
            )

            if hasattr(
                self.attention,
                "attention_weights"
            ):
                result["attention_weights"] = (
                    self.attention.attention_weights
                )

        return result