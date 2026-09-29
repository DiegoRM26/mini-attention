class LocationDataset:
    """
    Dataset pequeño para clasificar frases
    según la ubicación.

    0 -> casa
    1 -> oficina
    """

    def __init__(self):

        self.samples = [
            # -------------------------
            # CASA
            # -------------------------
            ("Yo estoy en casa", 0),
            ("Yo fui a casa", 0),
            ("Yo sali de la oficina y fui a casa", 0),
            ("Yo estoy en la casa", 0),
            ("Estoy en casa", 0),
            ("Estoy en la casa", 0),

            # -------------------------
            # OFICINA
            # -------------------------
            ("Yo estoy en la oficina", 1),
            ("Yo fui a la oficina", 1),
            ("Yo sali de casa y fui a la oficina", 1),
            ("Yo estoy en oficina", 1),
            ("Estoy en la oficina", 1),
            ("Estoy en oficina", 1),
        ]

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        return self.samples[index]

    def get_all(self):
        return self.samples