import numpy as np

from mini_attention.classifier import Classifier


# -----------------------------------------
# Representación ficticia de una frase
# -----------------------------------------

attention_output = np.array([
    [0.2, 0.4, 0.1, 0.3],
    [0.1, 0.5, 0.2, 0.2],
    [0.3, 0.2, 0.4, 0.1],
    [0.4, 0.1, 0.2, 0.3]
])


# -----------------------------------------
# Mean Pooling
# -----------------------------------------

sentence_vector = np.mean(
    attention_output,
    axis=0
)


print("Attention output:")
print(attention_output)

print("\nSentence vector:")
print(sentence_vector)

print("\nShape:")
print(sentence_vector.shape)


# -----------------------------------------
# Crear clasificador
# -----------------------------------------

classifier = Classifier(
    input_dim=4,
    num_classes=2
)


# -----------------------------------------
# Probabilidades
# -----------------------------------------

probabilities = classifier.predict_proba(
    sentence_vector
)


print("\nProbabilities:")
print(probabilities)


# -----------------------------------------
# Predicción
# -----------------------------------------

prediction = classifier.predict(
    sentence_vector
)


print("\nPredicted class:")
print(prediction)