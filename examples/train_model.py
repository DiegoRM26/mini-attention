from mini_attention.vocabulary import Vocabulary
from mini_attention.model import AttentionClassifier
from mini_attention.dataset import LocationDataset
from mini_attention.trainer import Trainer


# -----------------------------------------
# Vocabulary
# -----------------------------------------

vocab = Vocabulary()


# -----------------------------------------
# Dataset
# -----------------------------------------

dataset = LocationDataset()


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
# Trainer
# -----------------------------------------

trainer = Trainer(
    model,
    learning_rate=0.1
)


# -----------------------------------------
# Training
# -----------------------------------------

print("=" * 60)
print("TRAINING")
print("=" * 60)

history = trainer.train(
    dataset,
    epochs=100
)


# -----------------------------------------
# Results
# -----------------------------------------

print("\n")
print("=" * 60)
print("TRAINING COMPLETED")
print("=" * 60)

print("\nInitial loss:")
print(history[0])

print("\nFinal loss:")
print(history[-1])