from mini_attention.vocabulary import Vocabulary
from mini_attention.model import AttentionClassifier


# -----------------------------------------
# Vocabulary
# -----------------------------------------

vocab = Vocabulary()


# -----------------------------------------
# Model
# -----------------------------------------

model = AttentionClassifier(
    vocabulary=vocab,
    embedding_dim=8,
    attention_dim=4,
    num_classes=2
)


# -----------------------------------------
# Test sentences
# -----------------------------------------

sentences = [
    "Yo estoy en casa",
    "Yo estoy en la oficina",
    "Yo no estoy en casa",
    "Yo no estoy en la oficina",
]


# -----------------------------------------
# Predictions
# -----------------------------------------

for text in sentences:

    result = model.forward(
        text,
        return_attention=True
    )

    print("\n" + "=" * 60)

    print("Text:")
    print(text)

    print("\nTokens:")
    print(result["tokens"])

    print("\nSentence vector:")
    print(result["sentence_vector"])

    print("\nProbabilities:")
    print(result["probabilities"])

    print("\nPredicted class:")
    print(result["prediction"])