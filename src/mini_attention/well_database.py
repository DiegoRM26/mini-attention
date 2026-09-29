"""
Dataset consultable de intervenciones en pozos petroleros.

Provee una base de datos SQLite (con datos de ejemplo generados de forma
determinística) contra la cual se pueden ejecutar directamente las queries
SQL que produce `QueryBuilder`. El esquema de tablas y columnas coincide
exactamente con lo que `QueryBuilder` asume, incluyendo una vista
`well_events` que unifica todas las categorías para las preguntas que no
especifican un tipo de evento concreto.
"""

import random
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS well_perforations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id TEXT NOT NULL,
    event_type TEXT NOT NULL DEFAULT 'cañoneo',
    event_date TEXT NOT NULL,
    perforations_count INTEGER,
    shot_depth REAL,
    shot_density REAL
);

CREATE TABLE IF NOT EXISTS well_cleaning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_date TEXT NOT NULL,
    cleaning_type TEXT,
    volume_removed REAL
);

CREATE TABLE IF NOT EXISTS well_stimulation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id TEXT NOT NULL,
    event_type TEXT NOT NULL DEFAULT 'estimulación_mecánica',
    event_date TEXT NOT NULL,
    fluid_volume REAL,
    prop_mass REAL,
    injection_rate REAL
);

CREATE TABLE IF NOT EXISTS well_drilling (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id TEXT NOT NULL,
    event_type TEXT NOT NULL DEFAULT 'perforación',
    event_date TEXT NOT NULL,
    depth REAL,
    diameter REAL,
    duration_hours REAL
);

CREATE TABLE IF NOT EXISTS well_casing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    well_id TEXT NOT NULL,
    event_type TEXT NOT NULL DEFAULT 'revestimiento',
    event_date TEXT NOT NULL,
    diameter REAL,
    grade TEXT,
    connection_type TEXT
);
"""

# Vista genérica usada por QueryBuilder cuando la pregunta no especifica
# una categoría de evento concreta (columnas: well_id, event_type,
# event_date, description, details).
VIEW_SQL = """
CREATE VIEW IF NOT EXISTS well_events AS
SELECT
    well_id, event_type, event_date,
    'Cañoneo de ' || perforations_count || ' disparos a ' || shot_depth || 'm' AS description,
    'shot_density=' || shot_density AS details
FROM well_perforations
UNION ALL
SELECT
    well_id, event_type, event_date,
    'Limpieza (' || cleaning_type || ')' AS description,
    'volume_removed=' || volume_removed AS details
FROM well_cleaning
UNION ALL
SELECT
    well_id, event_type, event_date,
    'Estimulación mecánica' AS description,
    'fluid_volume=' || fluid_volume || ', prop_mass=' || prop_mass AS details
FROM well_stimulation
UNION ALL
SELECT
    well_id, event_type, event_date,
    'Perforación a ' || depth || 'm' AS description,
    'diameter=' || diameter || ', duration_hours=' || duration_hours AS details
FROM well_drilling
UNION ALL
SELECT
    well_id, event_type, event_date,
    'Revestimiento ' || grade AS description,
    'diameter=' || diameter || ', connection_type=' || connection_type AS details
FROM well_casing;
"""

# Pozos de ejemplo incluidos en el dataset (cubren los distintos formatos
# de ID soportados por EntityExtractor: cortos, con prefijo largo, etc.)
SAMPLE_WELLS = ["XX001", "XX002", "XX003", "XX004", "XX005", "CIRA001", "AB1234"]

DEFAULT_DB_PATH = Path(__file__).parent / "sample_data" / "wells.db"


class WellDatabase:
    """
    Envuelve una base de datos SQLite con el dataset de intervenciones
    en pozos y permite ejecutar directamente las queries generadas por
    `QueryBuilder`.
    """

    def __init__(self, db_path: Optional[str] = None, seed: int = 42, force_reseed: bool = False):
        """
        Args:
            db_path: Ruta al archivo SQLite. Usa ":memory:" para una base
                     efímera, o None para el archivo de datos de ejemplo
                     incluido con la librería (se crea si no existe).
            seed: Semilla para generar los datos de ejemplo de forma
                  reproducible.
            force_reseed: Si es True, borra y regenera los datos aunque
                           la base ya exista y tenga contenido.
        """
        if db_path is None:
            DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            db_path = str(DEFAULT_DB_PATH)

        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # SQLite no trae YEAR(); se emula para poder ejecutar el SQL tal
        # como lo genera QueryBuilder (pensado originalmente para MySQL).
        self.conn.create_function("YEAR", 1, _year_of)

        self._create_schema()
        if force_reseed or self._is_empty():
            self._reset_data()
            self._seed_data(seed)
            self._seed_anchor_examples()

    def _create_schema(self) -> None:
        self.conn.executescript(SCHEMA_SQL)
        self.conn.executescript(VIEW_SQL)
        self.conn.commit()

    def _is_empty(self) -> bool:
        cur = self.conn.execute("SELECT COUNT(*) FROM well_perforations")
        return cur.fetchone()[0] == 0

    def _reset_data(self) -> None:
        for table in ("well_perforations", "well_cleaning", "well_stimulation", "well_drilling", "well_casing"):
            self.conn.execute(f"DELETE FROM {table}")
        self.conn.commit()

    def _seed_data(self, seed: int) -> None:
        rng = random.Random(seed)

        for well_id in SAMPLE_WELLS:
            drilling_year = rng.randint(1998, 2015)

            # Perforación inicial del pozo
            self.conn.execute(
                "INSERT INTO well_drilling (well_id, event_type, event_date, depth, diameter, duration_hours) "
                "VALUES (?, 'perforación', ?, ?, ?, ?)",
                (
                    well_id,
                    f"{drilling_year}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                    round(rng.uniform(2500, 4500), 1),
                    round(rng.uniform(6, 12), 2),
                    round(rng.uniform(80, 300), 1),
                ),
            )

            # Revestimiento, poco después de perforar
            self.conn.execute(
                "INSERT INTO well_casing (well_id, event_type, event_date, diameter, grade, connection_type) "
                "VALUES (?, 'revestimiento', ?, ?, ?, ?)",
                (
                    well_id,
                    f"{drilling_year}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                    round(rng.uniform(5, 9), 2),
                    rng.choice(["K-55", "N-80", "P-110"]),
                    rng.choice(["BTC", "LTC", "VAM"]),
                ),
            )

            # Cañoneos: 2 a 4 eventos entre el año de perforación y 2025
            for _ in range(rng.randint(2, 4)):
                year = rng.randint(drilling_year + 1, 2025)
                self.conn.execute(
                    "INSERT INTO well_perforations "
                    "(well_id, event_type, event_date, perforations_count, shot_depth, shot_density) "
                    "VALUES (?, 'cañoneo', ?, ?, ?, ?)",
                    (
                        well_id,
                        f"{year}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                        rng.randint(8, 40),
                        round(rng.uniform(2800, 4200), 1),
                        round(rng.uniform(1.5, 4.0), 2),
                    ),
                )

            # Areneos y limpiezas: 2 a 4 eventos, mezclando ambas categorías
            for _ in range(rng.randint(2, 4)):
                year = rng.randint(drilling_year + 1, 2025)
                event_type = rng.choice(["araneo", "araneo", "limpieza"])
                self.conn.execute(
                    "INSERT INTO well_cleaning "
                    "(well_id, event_type, event_date, cleaning_type, volume_removed) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        well_id,
                        event_type,
                        f"{year}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                        rng.choice(["arena", "general", "residuos", "parafina"]),
                        round(rng.uniform(100, 600), 1),
                    ),
                )

            # Estimulación mecánica: 1 a 3 eventos
            for _ in range(rng.randint(1, 3)):
                year = rng.randint(drilling_year + 1, 2025)
                self.conn.execute(
                    "INSERT INTO well_stimulation "
                    "(well_id, event_type, event_date, fluid_volume, prop_mass, injection_rate) "
                    "VALUES (?, 'estimulación_mecánica', ?, ?, ?, ?)",
                    (
                        well_id,
                        f"{year}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                        round(rng.uniform(3000, 8000), 0),
                        round(rng.uniform(200000, 600000), 0),
                        round(rng.uniform(30, 70), 1),
                    ),
                )

        self.conn.commit()

    def _seed_anchor_examples(self) -> None:
        """
        Inserta un puñado de registros fijos (no aleatorios) que garantizan
        resultados no vacíos para las preguntas de ejemplo usadas en la app
        y en la documentación, sin afectar el resto de datos generados
        aleatoriamente para el resto del dataset.
        """
        self.conn.executemany(
            "INSERT INTO well_perforations "
            "(well_id, event_type, event_date, perforations_count, shot_depth, shot_density) VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("CIRA001", "cañoneo", "2025-03-10", 28, 3600.0, 2.8),
                ("XX001", "cañoneo", "2020-05-22", 20, 3400.0, 2.3),
                ("XX005", "cañoneo", "2021-06-18", 18, 3200.0, 2.6),
            ],
        )
        self.conn.executemany(
            "INSERT INTO well_cleaning "
            "(well_id, event_type, event_date, cleaning_type, volume_removed) VALUES (?, ?, ?, ?, ?)",
            [
                ("XX002", "araneo", "2003-09-02", "arena", 275.0),
                ("XX002", "araneo", "2008-04-14", "arena", 320.0),
                ("AB1234", "araneo", "2018-05-20", "arena", 410.0),
                ("XX004", "limpieza", "2021-03-11", "general", 180.0),
            ],
        )
        self.conn.executemany(
            "INSERT INTO well_stimulation "
            "(well_id, event_type, event_date, fluid_volume, prop_mass, injection_rate) VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("XX003", "estimulación_mecánica", "2019-07-01", 5200.0, 410000.0, 45.0),
                # Fecha posterior a cualquier evento aleatorio (tope 2025) para
                # que siempre gane como "el último" en las preguntas de tipo "last".
                ("XX003", "estimulación_mecánica", "2026-01-15", 6200.0, 480000.0, 55.0),
            ],
        )
        self.conn.commit()

    def execute(self, sql: str) -> List[Dict[str, Any]]:
        """
        Ejecuta una query SQL (tal como la produce QueryBuilder.build_query)
        contra el dataset y devuelve las filas como una lista de dicts.
        """
        cursor = self.conn.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def list_wells(self) -> List[str]:
        """Devuelve los IDs de pozo disponibles en el dataset."""
        cursor = self.conn.execute("SELECT DISTINCT well_id FROM well_events ORDER BY well_id")
        return [row[0] for row in cursor.fetchall()]

    def get_well_summary(self, well_id: str) -> List[Dict[str, Any]]:
        """Devuelve todos los eventos registrados para un pozo, más recientes primero."""
        return self.execute(
            f"SELECT well_id, event_type, event_date, description FROM well_events "
            f"WHERE well_id = '{well_id}' ORDER BY event_date DESC"
        )

    def total_records(self) -> int:
        """Número total de eventos en el dataset."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM well_events")
        return cursor.fetchone()[0]

    def close(self) -> None:
        self.conn.close()


def _year_of(date_str: Optional[str]) -> Optional[int]:
    """Extrae el año de una fecha 'YYYY-MM-DD' para emular YEAR() de SQL."""
    if not date_str:
        return None
    try:
        return int(str(date_str)[:4])
    except ValueError:
        return None
