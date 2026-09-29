import numpy as np
from typing import List, Tuple, Dict


class WellInterventionDataset:
    """
    Dataset específico para intervenciones en pozos petroleros.

    Contiene ejemplos de oraciones en lenguaje natural sobre:
    - Cañoneos
    - Areneos
    - Estimulación mecánica
    - Limpieza
    - Perforación
    - Revestimiento
    """

    def __init__(self, vocab=None):
        self.vocab = vocab
        self.examples = []
        self.labels = []
        self.texts = []
        self._load_well_data()

    def _load_well_data(self):
        """Carga datos de intervenciones en pozos."""
        self.examples = [
            # Cañoneos
            ("Al pozo XX001 cuantos cañoneos ha tenido en el año 2020", "perforations"),
            ("Pozo XX001 disparos realizados 2020", "perforations"),
            ("Cuantos cañoneos se han ejecutado en XX002 durante 2019 y 2020", "perforations"),
            ("XX003 perforaciones desde 2000 hasta 2010", "perforations"),
            ("Cantidad de disparos en pozo XX004", "perforations"),

            # Areneos
            ("Cuantos areneos a tenido el pozo XX002 desde el año 2000 y 2010", "cleaning"),
            ("Limpieza de arena en XX001 año 2021", "cleaning"),
            ("XX003 cuantas limpiezas de arena se han realizado", "cleaning"),
            ("Pozo XX004 arena removida 2018", "cleaning"),
            ("Areneos realizados en XX002", "cleaning"),

            # Estimulación mecánica
            ("Que estimulación mecanica fue la ultima aplicada en el pozo XX003", "stimulation"),
            ("XX001 fractura hidráulica última 2021", "stimulation"),
            ("Pozo XX002 estimulación mecánica efectuada entre 2015 y 2020", "stimulation"),
            ("XX003 procedimientos de fracturamiento", "stimulation"),
            ("Cuantas estimulaciones ha tenido XX004", "stimulation"),

            # Combinadas
            ("XX001 cañoneos y areneos en 2020", "combined"),
            ("Pozo XX002 intervenciones desde 2000 hasta 2022", "combined"),
            ("XX003 perforaciones estimulación y limpieza", "combined"),
            ("Que operaciones se realizaron en XX001 durante 2010", "combined"),
            ("Historial completo de intervenciones en pozo XX002", "combined"),

            # Otras operaciones
            ("Revestimiento del pozo XX001 año 2015", "casing"),
            ("XX002 perforación completada en 2019", "drilling"),
            ("Pozo XX003 trabajos de mantenimiento 2021", "maintenance"),
            ("XX004 reparación de línea 2020", "repair"),
        ]

        self.labels = [label for _, label in self.examples]
        self.texts = [text for text, _ in self.examples]

    @property
    def classes(self) -> List[str]:
        """Retorna clases de intervención disponibles."""
        return [
            "perforations",    # Cañoneos/disparos
            "cleaning",        # Areneos/limpieza
            "stimulation",     # Estimulación mecánica
            "casing",          # Revestimiento
            "drilling",        # Perforación
            "maintenance",     # Mantenimiento
            "repair",          # Reparación
            "combined",        # Operaciones combinadas
        ]

    def __len__(self) -> int:
        """Retorna número de ejemplos."""
        return len(self.texts)

    def __getitem__(self, idx: int) -> Tuple[str, int]:
        """Retorna un ejemplo y su label."""
        text = self.texts[idx]
        label = self.labels[idx]
        label_id = self.classes.index(label)
        return text, label_id

    def get_by_class(self, class_name: str) -> List[str]:
        """Retorna todos los ejemplos de una clase específica."""
        return [text for text, label in zip(self.texts, self.labels) if label == class_name]

    def get_statistics(self) -> Dict:
        """Retorna estadísticas del dataset."""
        stats = {
            "total_examples": len(self.texts),
            "num_classes": len(self.classes),
            "class_distribution": {},
            "avg_text_length": np.mean([len(t.split()) for t in self.texts]),
        }

        for class_name in self.classes:
            count = sum(1 for label in self.labels if label == class_name)
            stats["class_distribution"][class_name] = count

        return stats


class WellDataLoader:
    """
    Data loader para el dataset de pozos.
    Proporciona batches de ejemplos para entrenamiento.
    """

    def __init__(self, dataset: WellInterventionDataset, batch_size: int = 4, shuffle: bool = True):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indices = np.arange(len(dataset))

    def __iter__(self):
        """Itera sobre batches del dataset."""
        if self.shuffle:
            np.random.shuffle(self.indices)

        for i in range(0, len(self.dataset), self.batch_size):
            batch_indices = self.indices[i:i + self.batch_size]
            batch_texts = [self.dataset.texts[idx] for idx in batch_indices]
            batch_labels = [self.dataset.labels[idx] for idx in batch_indices]
            yield batch_texts, batch_labels

    def __len__(self) -> int:
        """Retorna número de batches."""
        return len(self.dataset) // self.batch_size + (1 if len(self.dataset) % self.batch_size else 0)
