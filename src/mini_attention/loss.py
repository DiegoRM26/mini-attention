import numpy as np


def cross_entropy(
    probabilities,
    target
):
    """
    Calcula Cross-Entropy Loss
    para una clasificación.

    Parameters
    ----------
    probabilities : np.ndarray
        Probabilidades predichas por el modelo.

    target : int
        Clase correcta.

    Returns
    -------
    float
        Valor de la pérdida.
    """

    probabilities = np.asarray(
        probabilities
    )

    # Evitamos log(0)
    probabilities = np.clip(
        probabilities,
        1e-12,
        1.0
    )

    return -np.log(
        probabilities[target]
    )