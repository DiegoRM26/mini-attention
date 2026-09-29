import numpy as np


def softmax(x, axis=-1):

    x = x - np.max(x, axis=axis, keepdims=True)

    exp_x = np.exp(x)

    return exp_x / np.sum(
        exp_x,
        axis=axis,
        keepdims=True
    )


def scaled_dot_product(Q, K):

    d_k = K.shape[-1]

    return (Q @ K.T) / np.sqrt(d_k)


def attention_output(attention_weights, v):
    return np.dot(attention_weights, v)


def mse_loss(prediction, target):
    return np.mean((prediction - target) ** 2)

def numerical_gradient(model, tokens, target, epsilon=1e-5):
    gradients = {}

    for name in ["W_q", "W_k", "W_v"]:

        weights = getattr(model, name)

        gradient = np.zeros_like(weights)

        for i in range(weights.shape[0]):
            for j in range(weights.shape[1]):

                original_value = weights[i, j]

                weights[i, j] = original_value + epsilon

                prediction_plus = model(tokens)
                loss_plus = mse_loss(prediction_plus, target)

                weights[i, j] = original_value

                prediction = model(tokens)
                loss = mse_loss(prediction, target)

                gradient[i, j] = (
                    loss_plus - loss
                ) / epsilon

        gradients[name] = gradient

    return gradients