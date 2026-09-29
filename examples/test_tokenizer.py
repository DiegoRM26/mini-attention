from mini_attention.vocabulary import Vocabulary
from mini_attention.tokenizer import Tokenizer


vocab = Vocabulary()

tokenizer = Tokenizer(vocab)


text = "Yo no estoy en la oficina."


print("Original text:")
print(text)


print("\nTokens:")
print(tokenizer.tokenize(text))


print("\nToken IDs:")
print(tokenizer.encode(text))


print("\nDecoded:")
print(
    tokenizer.decode(
        tokenizer.encode(text)
    )
)