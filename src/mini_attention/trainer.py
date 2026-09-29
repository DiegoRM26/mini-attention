import numpy as np

from .loss import cross_entropy


class Trainer:
    """
    Entrenador del modelo.

    En esta etapa entrenamos únicamente
    los pesos del Classifier.

    Attention y Embeddings permanecen congelados.
    """

    def __init__(
        self,
        model,
        learning_rate=0.1
    ):

        self.model = model
        self.learning_rate = learning_rate

    def train_step(
        self,
        text,
        target
    ):
        """
        Calcula el gradiente de una muestra
        y devuelve la información necesaria.
        """

        # -----------------------------------------
        # Forward
        # -----------------------------------------

        result = self.model.forward(text)

        sentence_vector = result[
            "sentence_vector"
        ]

        probabilities = result[
            "probabilities"
        ]

        # -----------------------------------------
        # Loss
        # -----------------------------------------

        loss = cross_entropy(
            probabilities,
            target
        )

        # -----------------------------------------
        # Gradient
        # -----------------------------------------

        gradient_logits = probabilities.copy()

        gradient_logits[target] -= 1

        # -----------------------------------------
        # Gradient W
        # -----------------------------------------

        gradient_weights = np.outer(
            sentence_vector,
            gradient_logits
        )

        # -----------------------------------------
        # Gradient bias
        # -----------------------------------------

        gradient_bias = gradient_logits

        return (
            loss,
            gradient_weights,
            gradient_bias
        )

    def train(
        self,
        dataset,
        epochs=100,
        verbose=True
    ):

        history = []

        # -----------------------------------------
        # Dataset
        # -----------------------------------------

        samples = dataset.get_all()

        # -----------------------------------------
        # Training loop
        # -----------------------------------------

        for epoch in range(
            1,
            epochs + 1
        ):

            total_loss = 0.0

            total_gradient_weights = np.zeros_like(
                self.model.classifier.weights
            )

            total_gradient_bias = np.zeros_like(
                self.model.classifier.bias
            )

            # -------------------------------------
            # Calculate gradients
            # -------------------------------------

            for text, target in samples:

                (
                    loss,
                    gradient_weights,
                    gradient_bias
                ) = self.train_step(
                    text,
                    target
                )

                total_loss += loss

                total_gradient_weights += (
                    gradient_weights
                )

                total_gradient_bias += (
                    gradient_bias
                )

            # -------------------------------------
            # Average gradients
            # -------------------------------------

            n = len(samples)

            average_gradient_weights = (
                total_gradient_weights / n
            )

            average_gradient_bias = (
                total_gradient_bias / n
            )

            # -------------------------------------
            # Update
            # -------------------------------------

            self.model.classifier.weights -= (
                self.learning_rate
                * average_gradient_weights
            )

            self.model.classifier.bias -= (
                self.learning_rate
                * average_gradient_bias
            )

            # -------------------------------------
            # Average loss
            # -------------------------------------

            average_loss = (
                total_loss / n
            )

            history.append(
                average_loss
            )

            # -------------------------------------
            # Progress
            # -------------------------------------

            if verbose:

                if (
                    epoch == 1
                    or epoch % 10 == 0
                    or epoch == epochs
                ):

                    print(
                        f"Epoch {epoch:3d} "
                        f"| Loss: "
                        f"{average_loss:.6f}"
                    )

        return history

    def fit(self, tokens, target, epochs=100, verbose=True):
        """
        API alternativa para entrenamiento directo.

        Parametros:
        -----------
        tokens : list de str o str
            Muestras (frases/tokens)
        target : np.ndarray
            Target (matrix o vector de clases)
        epochs : int
            Numero de epocas
        verbose : bool
            Mostrar progreso

        Returns:
        --------
        history : list
            Historial de perdidas por epoca
        """

        # Validar que tokens y target tienen la misma longitud
        if isinstance(tokens, str):
            tokens = [tokens]

        target = np.asarray(target)

        if len(tokens) != len(target):
            raise ValueError(
                f"tokens tiene {len(tokens)} muestras "
                f"pero target tiene {len(target)}"
            )

        # Si target es 2D (one-hot), convertir a indices de clase
        # ya que train_step espera un indice entero.
        if target.ndim == 2:
            target = np.argmax(target, axis=1)

        # Crear un dataset simple (lista de tuplas)
        class SimpleDataset:
            def __init__(self, samples):
                self.samples = samples

            def get_all(self):
                return self.samples

        # Convertir tokens y target a dataset
        samples = list(zip(tokens, target))
        dataset = SimpleDataset(samples)

        # Usar train() interno
        return self.train(
            dataset,
            epochs=epochs,
            verbose=verbose
        )

    def predict(self, X):
        """
        Realizar prediccion sobre muestras.

        Parametros:
        -----------
        X : list de str o str
            Muestras para prediccion

        Returns:
        --------
        predictions : np.ndarray
            Predicciones del modelo
        """

        # Manejar entrada escalar o lista
        if isinstance(X, str):
            X = [X]

        predictions = []

        for text in X:
            result = self.model.forward(text)

            # Extraer prediccion segun si es dict o ndarray
            if isinstance(result, dict):
                # Preferir "prediction" (AttentionClassifier),
                # luego "output" (SelfAttention con return_attention),
                # luego mean pooling manual.
                if "prediction" in result:
                    pred = result["prediction"]
                elif "output" in result:
                    output = result["output"]
                    sentence_vector = np.mean(output, axis=0)
                    if hasattr(self.model, "classifier"):
                        pred = self.model.classifier.predict(
                            sentence_vector
                        )
                    else:
                        pred = sentence_vector
                else:
                    pred = result
            else:
                # ndarray directo desde SelfAttention.forward()
                if hasattr(self.model, "classifier"):
                    sentence_vector = np.mean(result, axis=0)
                    pred = self.model.classifier.predict(
                        sentence_vector
                    )
                else:
                    pred = result

            predictions.append(pred)

        return np.array(predictions)