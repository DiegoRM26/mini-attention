import numpy as np

from mini_attention import AttentionClassifier, SelfAttention, Trainer, Vocabulary


def test_attention_weights_are_a_distribution():
    model = SelfAttention(vocabulary=Vocabulary(), seed=42)
    result = model("Pozo XX001 cañoneos 2020", return_attention=True)
    weights = result["attention_weights"]
    assert weights.shape[0] == weights.shape[1] == len(result["tokens"])
    assert np.allclose(weights.sum(axis=-1), 1.0)
    assert (weights >= 0).all()


def test_attention_is_reproducible_with_seed():
    a = SelfAttention(vocabulary=Vocabulary(), seed=7)("yo estoy en casa")
    b = SelfAttention(vocabulary=Vocabulary(), seed=7)("yo estoy en casa")
    assert np.allclose(a, b)


def test_classifier_outputs_probabilities():
    model = AttentionClassifier(Vocabulary(), num_classes=3)
    out = model.forward("Pozo XX001 cañoneos", return_attention=True)
    assert "prediction" in out
    assert 0 <= out["prediction"] < 3


def test_training_reduces_loss():
    class DS:
        def __init__(self, samples):
            self.samples = samples

        def get_all(self):
            return self.samples

    np.random.seed(0)
    model = AttentionClassifier(Vocabulary(), num_classes=2)
    data = DS([("yo estoy en casa", 0),
               ("tu estas en la oficina", 1)])
    trainer = Trainer(model=model, learning_rate=0.1)
    from mini_attention.loss import cross_entropy

    def loss():
        return sum(cross_entropy(model.forward(t)["probabilities"], y) for t, y in data.get_all())

    before = loss()
    trainer.train(dataset=data, epochs=50)
    assert loss() < before
