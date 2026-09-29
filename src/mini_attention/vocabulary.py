from .tokenizer import Tokenizer


class Vocabulary:

    def __init__(self, words=None):

        if words is None:
            words = [
                "Yo",
                "Tú",
                "Estoy",
                "Estás",
                "Voy",
                "En",
                "A",
                "De",
                "La",
                "El",
                "Casa",
                "Oficina",
                "Trabajo",
                "Escuela",
                "Salí",
                "Fui",
                "No"
            ]

        # Token especial para palabras desconocidas
        self.unk_token = "<UNK>"

        # Vocabulario completo
        self.words = words + [self.unk_token]

        # Tokenizer
        self.tokenizer = Tokenizer(self)
        self.size = len(self.words)

        # Palabra → ID
        self.word_to_id = {}

        for index, word in enumerate(self.words):

            # Los tokens especiales mantienen su nombre original
            if word == self.unk_token:
                key = word
            else:
                key = word.lower()

            self.word_to_id[key] = index

        # ID → palabra
        self.id_to_word = {
            index: word
            for index, word in enumerate(self.words)
        }

    def encode(self, word):
        """
        Convierte una palabra en su ID.

        La búsqueda no distingue entre mayúsculas
        y minúsculas.
        """

        normalized_word = word.lower()

        return self.word_to_id.get(
            normalized_word,
            self.word_to_id[self.unk_token]
        )

    def decode(self, index):
        """
        Convierte un ID nuevamente en una palabra.
        """

        return self.id_to_word.get(
            index,
            self.unk_token
        )

    def __len__(self):
        """
        Devuelve el tamaño del vocabulario.
        """

        return len(self.words)