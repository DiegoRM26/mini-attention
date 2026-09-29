from mini_attention.dataset import LocationDataset


dataset = LocationDataset()


print("Dataset size:")
print(len(dataset))


print("\nSamples:")

for text, label in dataset.get_all():

    class_name = (
        "casa"
        if label == 0
        else "oficina"
    )

    print(
        f"{text} -> "
        f"{label} ({class_name})"
    )