import numpy as np

from mini_attention.vocabulary import Vocabulary
from mini_attention.model import AttentionClassifier
from mini_attention.loss import cross_entropy


# -----------------------------------------
# Vocabulary
# -----------------------------------------

vocabulary = Vocabulary()


# -----------------------------------------
# Model
# -----------------------------------------

model = AttentionClassifier(
    vocabulary=vocabulary,
    embedding_dim=8,
    attention_dim=4,
    num_classes=2
)


# -----------------------------------------
# Test sample
# -----------------------------------------

text = "Yo estoy en casa"

target = 0


# -----------------------------------------
# Forward BEFORE update
# -----------------------------------------

result = model.forward(text)

sentence_vector = result["sentence_vector"]
probabilities = result["probabilities"]

loss_before = cross_entropy(
    probabilities,
    target
)


print("Text:")
print(text)

print("\nTarget:")
print(target)

print("\nSentence vector:")
print(sentence_vector)

print("\nProbabilities BEFORE:")
print(probabilities)

print("\nLoss BEFORE:")
print(loss_before)


# -----------------------------------------
# Calculate gradient
# -----------------------------------------

gradient_logits = probabilities.copy()

gradient_logits[target] -= 1


gradient_weights = np.outer(
    sentence_vector,
    gradient_logits
)

gradient_bias = gradient_logits


# -----------------------------------------
# Update
# -----------------------------------------

learning_rate = 0.05

model.classifier.weights -= (
    learning_rate
    * gradient_weights
)

model.classifier.bias -= (
    learning_rate
    * gradient_bias
)


# -----------------------------------------
# Forward AFTER update
# -----------------------------------------

result_after = model.forward(text)

probabilities_after = result_after[
    "probabilities"
]

loss_after = cross_entropy(
    probabilities_after,
    target
)


print("\n=============================")

print("\nProbabilities AFTER:")
print(probabilities_after)

print("\nLoss AFTER:")
print(loss_after)

print("\n=============================")

print("\nLoss change:")

print(
    loss_after - loss_before
)