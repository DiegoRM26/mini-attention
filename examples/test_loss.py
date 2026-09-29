import numpy as np

from mini_attention.loss import cross_entropy


# -----------------------------------------
# Predicción incorrecta
# -----------------------------------------

probabilities = np.array([
    0.50,
    0.50
])

target = 0

loss = cross_entropy(
    probabilities,
    target
)

print("Probabilities:")
print(probabilities)

print("\nTarget:")
print(target)

print("\nLoss:")
print(loss)


# -----------------------------------------
# Predicción mejor
# -----------------------------------------

probabilities = np.array([
    0.90,
    0.10
])

loss = cross_entropy(
    probabilities,
    target
)

print("\n-----------------------------")

print("\nBetter prediction:")
print(probabilities)

print("\nLoss:")
print(loss)