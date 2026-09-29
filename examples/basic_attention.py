import numpy as np

from mini_attention import AttentionClassifier, Trainer, Vocabulary
from mini_attention.loss import cross_entropy


# -----------------------------------
# Reproducibilidad
# -----------------------------------

np.random.seed(42)


# -----------------------------------
# Crear Vocabulario
# -----------------------------------

vocab = Vocabulary()


# -----------------------------------
# Datos de entrenamiento
# -----------------------------------

texts = [
    "Yo estoy en casa",
    "Tu estás en la oficina",
    "Yo estoy trabajando"
]

# Clase objetivo (índice entero) de cada texto
targets = np.array([0, 1, 0])


# -----------------------------------
# Crear modelo
# -----------------------------------

model = AttentionClassifier(vocabulary=vocab, num_classes=2)


# -----------------------------------
# Crear Trainer
# -----------------------------------

trainer = Trainer(
    model=model,
    learning_rate=0.1
)


# -----------------------------------
# Entrenar
# -----------------------------------

class SimpleDataset:
    def __init__(self, texts, targets):
        self.samples = list(zip(texts, targets))

    def get_all(self):
        return self.samples


dataset = SimpleDataset(texts, targets)

trainer.train(
    dataset=dataset,
    epochs=100
)


# -----------------------------------
# Realizar predicción
# -----------------------------------

output = model.forward(texts[0])["probabilities"]


# -----------------------------------
# Calcular Loss final
# -----------------------------------

final_loss = cross_entropy(
    output,
    targets[0]
)


# -----------------------------------
# Mostrar resultados
# -----------------------------------

print("\n-----------------------------------")
print("Training completed")
print("-----------------------------------")

print("\nTexts:")
for i, text in enumerate(texts):
    print(f"  {i}: {text}")

print("\nTargets:")
print(targets)

print("\nFinal output (texto 0):")
print(output)

print("\nFinal loss:")
print(final_loss)
