from mini_attention.model import AttentionClassifier
from mini_attention.vocabulary import Vocabulary


vocabulary = Vocabulary()

model = AttentionClassifier(
    vocabulary=vocabulary
)


texts = [
    "Yo estoy en casa",
    "Yo estoy en la oficina"
]


for text in texts:

    result = model.forward(text)

    print("\n" + "=" * 50)
    print("Texto:")
    print(text)

    print("\nSentence vector:")
    print(result["sentence_vector"])

    print("\nProbabilidades:")
    print(result["probabilities"])