from mini_attention.vocabulary import Vocabulary


vocab = Vocabulary()


print("Vocabulary size:")
print(len(vocab))


print("\nWord to ID:")

for word in [
    "Yo",
    "Tú",
    "Estoy",
    "Casa",
    "Oficina",
    "No"
]:
    print(f"{word} -> {vocab.encode(word)}")


print("\nID to Word:")

for index in range(len(vocab)):
    print(f"{index} -> {vocab.decode(index)}")


print("\nUnknown word:")

print(
    "Perro ->",
    vocab.encode("Perro")
)