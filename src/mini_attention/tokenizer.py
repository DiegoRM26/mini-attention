import re


class Tokenizer:

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary

    def tokenize(self, text):
        """
        Convierte una frase en una lista de tokens.

        Ejemplo:
        "Yo no estoy en la oficina"
        ->
        ["Yo", "no", "estoy", "en", "la", "oficina"]
        """

        # Normalizamos espacios
        text = text.strip()

        # Eliminamos puntuación básica
        text = re.sub(r"[.,!?;:¿¡]", "", text)

        # Separamos por espacios
        tokens = text.split()

        return tokens

    def encode(self, text):
        """
        Convierte una frase directamente en IDs.

        Ejemplo:
        "Yo no estoy en la oficina"
        ->
        [0, 16, 2, 5, 8, 11]
        """

        tokens = self.tokenize(text)

        return [
            self.vocabulary.encode(token)
            for token in tokens
        ]

    def tokenize_to_ids(self, text):
        """
        Alias de encode() para compatibilidad con attention.py.

        Convierte una frase directamente en IDs.
        """
        return self.encode(text)

    def decode(self, token_ids):
        """
        Convierte IDs nuevamente en una frase.
        """

        tokens = [
            self.vocabulary.decode(token_id)
            for token_id in token_ids
        ]

        return " ".join(tokens)