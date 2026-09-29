import numpy as np


class Classifier:
    """
    Clasificador lineal sencillo.

    Recibe una representación vectorial y produce
    una puntuación para cada clase.
    """

    def __init__(
        self,
        input_dim,
        num_classes,
        seed=42
    ):
        """
        Parameters
        ----------
        input_dim : int
            Dimensión del vector de entrada.

        num_classes : int
            Número de clases.

        seed : int
            Semilla para inicializar los pesos.
        """

        rng = np.random.default_rng(seed)

        # Pesos
        self.weights = rng.normal(
            0,
            0.1,
            size=(input_dim, num_classes)
        )

        # Bias
        self.bias = np.zeros(
            num_classes
        )

    def forward(self, x):
        """
        Calcula los logits.

        x:
            Vector de entrada.

        Returns
        -------
        logits:
            Puntuaciones para cada clase.
        """

        x = np.asarray(x)

        return x @ self.weights + self.bias

    def softmax(self, logits):
        """
        Convierte logits en probabilidades.
        """

        logits = np.asarray(logits)

        # Estabilidad numérica
        shifted = logits - np.max(
            logits,
            axis=-1,
            keepdims=True
        )

        exp_values = np.exp(
            shifted
        )

        probabilities = (
            exp_values
            / np.sum(
                exp_values,
                axis=-1,
                keepdims=True
            )
        )

        return probabilities

    def predict_proba(self, x):
        """
        Devuelve las probabilidades
        de cada clase.
        """

        logits = self.forward(x)

        return self.softmax(
            logits
        )

    def predict(self, x):
        """
        Devuelve la clase con mayor probabilidad.
        """

        probabilities = self.predict_proba(
            x
        )

        return np.argmax(
            probabilities,
            axis=-1
        )