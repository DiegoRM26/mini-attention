# mini-attention: Educational Self-Attention Library

Una pequeña biblioteca educativa para aprender **Self-Attention** paso a paso, con un módulo especializado para extracción de información en intervenciones de pozos petroleros.

---

## Características

- Implementación de **Scaled Dot-Product Self-Attention**
- **Extracción de entidades** de lenguaje natural usando patrones + atención
- **Generación automática de queries SQL** basada en entidades extraídas
- Dataset especializado en intervenciones de pozos petroleros
- Clasificación de tipos de intervención (cañoneos, areneos, estimulación, etc.)
- Visualización de pesos de atención
- Soporte para entrenamiento y evaluación
- Ejemplos completos y documentación

---

## Instalación

```bash
git clone <url-del-repo> && cd mini_attention
pip install -e ".[app]"      # librería + app Streamlit
pip install -e ".[dev]"      # además pytest, para desarrollo
```

## App de chat (Streamlit)

Asistente que lee los datos de prueba (SQLite generado con semilla fija por
`WellDatabase`) y responde preguntas en lenguaje natural: extrae pozo, evento y
fechas, pide aclaración si falta información, genera el SQL y lo ejecuta.

```bash
streamlit run app.py
```

## Tests

```bash
pytest
```

---

## Uso Rápido

### 1. Extracción de Información en Pozos (Nuevo)

```python
from mini_attention import EntityExtractor, QueryBuilder

# Crear extractores
extractor = EntityExtractor()
builder = QueryBuilder(db_type="postgresql")

# Procesar pregunta en lenguaje natural
query = "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020"
entities = extractor.extract(query)
formatted = extractor.format_for_query(entities)

print(entities)
# {
#   'wells': [{'id': 'XX001', 'position': 8, 'confidence': 0.95}],
#   'events': [{'type': 'cañoneo', 'text': 'cañoneos', ...}],
#   'dates': [{'type': 'year', 'year': 2020, ...}],
# }

# Generar SQL automáticamente
sql = builder.build_query(formatted)
print(sql)

# Obtener resumen en lenguaje natural
summary = builder.get_summary(formatted)
print(summary)
# "Query busca: pozos XX001 | Eventos: cañoneo | Año: 2020"

# Obtener resultados simulados
results = builder.get_mock_results(formatted)
```

### 2. Clasificación de Intervenciones

```python
from mini_attention import WellInterventionDataset, Vocabulary, AttentionClassifier

# Cargar dataset especializado
dataset = WellInterventionDataset()

# Ver estadísticas
stats = dataset.get_statistics()
print(f"Total ejemplos: {stats['total_examples']}")
print(f"Clases: {stats['class_distribution']}")

# Crear modelo clasificador
vocab = Vocabulary()
for text in dataset.texts:
    vocab.add_text(text)

model = AttentionClassifier(vocabulary=vocab, num_classes=len(dataset.classes))

# Clasificar nuevo texto
result = model.forward(
    "Estimulación mecánica en pozo XX003",
    return_attention=True
)
predicted_class = dataset.classes[result["prediction"]]
print(f"Tipo de intervención: {predicted_class}")
```

### 3. Self-Attention Básico

```python
from mini_attention import Vocabulary, SelfAttention

vocab = Vocabulary()
model = SelfAttention(vocabulary=vocab)

# Obtener pesos de atención
result = model("Yo estoy en casa", return_attention=True)
print("Tokens:", result["tokens"])
print("Attention Weights:", result["attention_weights"])
print("Output:", result["output"])
```

### 4. Visualizar Atención

```python
from mini_attention import Vocabulary, SelfAttention
from mini_attention.visualization import plot_attention
import matplotlib.pyplot as plt

vocab = Vocabulary()
model = SelfAttention(vocabulary=vocab)

result = model("Pozo XX001 cañoneos 2020", return_attention=True)

plot_attention(
    tokens=result["tokens"],
    attention_weights=result["attention_weights"],
    title="Self-Attention Weights"
)
plt.show()
```

---

## Arquitectura General

```
        Texto en Lenguaje Natural
                  |
                  v
            Entity Extractor (Patrones + Regex)
                  |
        +---------+---------+
        |         |         |
        v         v         v
     Pozos    Eventos    Fechas
        |         |         |
        +----+----+----+----+
             |
             v
        Query Builder
             |
             v
        SQL Query / Resultados
```

---

## Componentes Principales

### 1. EntityExtractor
Extrae entidades de texto en lenguaje natural:

| Entidad  | Patrón               | Ejemplo                |
|----------|----------------------|------------------------|
| Pozos    | `XX001`, `AB002`     | "pozo XX001"           |
| Eventos  | cañoneo, araneo, etc | "cañoneos realizados"  |
| Fechas   | Años, rangos         | "2020", "2000-2010"    |

```python
extractor = EntityExtractor()
entities = extractor.extract("Pozo XX001 cañoneos 2020-2021")
# {
#   'wells': [{'id': 'XX001', ...}],
#   'events': [{'type': 'cañoneo', ...}],
#   'dates': [{'type': 'year_range', 'start': 2020, 'end': 2021}],
# }
```

### 2. QueryBuilder
Genera queries SQL y consultas en lenguaje natural:

```python
builder = QueryBuilder(db_type="postgresql")

# Generar SQL
sql = builder.build_query(formatted_entities)

# Obtener resumen en lenguaje natural
summary = builder.get_summary(formatted_entities)

# Obtener resultados de ejemplo (simulación)
results = builder.get_mock_results(formatted_entities)
```

### 3. WellDatabase
Dataset consultable de verdad (SQLite, generado de forma reproducible) contra
el que se ejecutan directamente las queries producidas por `QueryBuilder`:

```python
from mini_attention import WellDatabase

db = WellDatabase(seed=42)  # crea/reutiliza src/mini_attention/sample_data/wells.db

db.list_wells()                    # ['AB1234', 'CIRA001', 'XX001', ...]
db.total_records()                 # número total de eventos
db.get_well_summary("XX001")       # historial completo de un pozo

# Ejecutar directamente el SQL que genera QueryBuilder
rows = db.execute(sql)
```

Incluye tablas por categoría (`well_perforations`, `well_cleaning`,
`well_stimulation`, `well_drilling`, `well_casing`) y una vista `well_events`
que las unifica para las preguntas sin categoría específica. Trae ~80
eventos generados con semilla fija (reproducibles) sobre 7 pozos de ejemplo.

### 4. WellInterventionDataset
Dataset especializado con 25+ ejemplos para clasificación (no confundir con
`WellDatabase`, que es el dataset consultable vía SQL):

| Clase | Descripción | Ejemplos |
|-------|-------------|----------|
| `perforations` | Cañoneos/disparos | 5 |
| `cleaning` | Areneos/limpieza | 5 |
| `stimulation` | Estimulación mecánica | 5 |
| `combined` | Operaciones combinadas | 3 |
| `casing` | Revestimiento | 1 |
| `drilling` | Perforación | 1 |
| `maintenance` | Mantenimiento | 1 |
| `repair` | Reparación | 1 |

### 5. SelfAttention (Original)
Implementación de Scaled Dot-Product Self-Attention:

```python
Attention(Q, K, V) = softmax(Q · K^T / sqrt(d_k)) · V
```

### 5. AttentionClassifier (Original)
Pipeline completo: Embedding → Self-Attention → Clasificador Lineal

### 6. Trainer (Original)
Entrena los pesos del clasificador usando SGD

---

## Tipos de Intervención Soportados

```
┌─────────────────────────────────────────────────────┐
│  INTERVENCIONES EN POZOS PETROLEROS                  │
├─────────────────────────────────────────────────────┤
│                                                       │
│  • Cañoneos (Perforations)                           │
│    └─ Disparos controlados en la zona de interés    │
│                                                       │
│  • Areneos (Cleaning)                               │
│    └─ Remoción de arena y residuos                   │
│                                                       │
│  • Estimulación Mecánica (Stimulation)              │
│    └─ Fracturamiento hidráulico                      │
│                                                       │
│  • Limpieza (Cleaning)                              │
│    └─ Limpieza general del pozo                      │
│                                                       │
│  • Perforación (Drilling)                           │
│    └─ Creación de nuevos pozos o secciones           │
│                                                       │
│  • Revestimiento (Casing)                           │
│    └─ Instalación de tubería de revestimiento        │
│                                                       │
│  • Mantenimiento (Maintenance)                      │
│    └─ Operaciones de mantenimiento rutinario         │
│                                                       │
│  • Reparación (Repair)                              │
│    └─ Corrección de problemas operacionales           │
│                                                       │
└─────────────────────────────────────────────────────┘
```

---

## Ejemplos de Preguntas Soportadas

### Consultas Simples
- "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020"
- "Cuantos areneos a tenido el pozo XX002 desde el año 2000 y 2010"
- "Que estimulación mecanica fue la ultima aplicada en el pozo XX003"

### Consultas Complejas
- "XX001 cañoneos y areneos en 2020"
- "Pozo XX002 intervenciones desde 2000 hasta 2022"
- "Historial completo de intervenciones en pozo XX002"

---

## Ejemplos Completos

Vea la carpeta `examples/` para ejemplos completos:

### Nuevos (Well Intervention)
- **`well_intervention_example.py`** — Pipeline completo con 5 ejemplos:
  1. Extracción de entidades
  2. Generación de queries SQL
  3. Clasificación de intervenciones
  4. Pipeline end-to-end
  5. Clasificación con atención

### Originales
- `basic_attention.py` — Ejemplo mínimo de Self-Attention
- `test_attention.py` — Pruebas del componente de atención
- `test_model.py` — Pruebas del modelo completo
- `train_model.py` — Entrenamiento completo
- `visualize_attention.py` — Generar visualizaciones
- `compare_attention.py` — Comparar atención entre frases

### Ejecutar ejemplos

```bash
# Ejemplo completo de intervenciones en pozos
python examples/well_intervention_example.py

# Ejemplos originales
python examples/basic_attention.py
python examples/train_model.py
python examples/visualize_attention.py
```

---

## Parámetros

### EntityExtractor

```python
extractor = EntityExtractor()

# Extraer entidades con soporte para pesos de atención
entities = extractor.extract(
    text="Pozo XX001 cañoneos 2020",
    attention_weights=None  # Opcional: matriz de pesos de atención
)

# Formatear para query builder
formatted = extractor.format_for_query(entities)
```

### QueryBuilder

```python
builder = QueryBuilder(db_type="postgresql")  # postgresql, mysql, sqlite

# Generar query
sql = builder.build_query(formatted_entities)

# Obtener resumen
summary = builder.get_summary(formatted_entities)

# Obtener resultados de ejemplo
results = builder.get_mock_results(formatted_entities)
```

### WellInterventionDataset

```python
dataset = WellInterventionDataset(vocab=None)

# Acceder a datos
text, label_id = dataset[0]

# Obtener ejemplos por clase
examples = dataset.get_by_class("perforations")

# Estadísticas
stats = dataset.get_statistics()
```

### SelfAttention (Original)

```python
model = SelfAttention(
    vocabulary,        # Objeto Vocabulary (requerido)
    embedding_dim=8,   # Dimensión de embeddings
    attention_dim=4,   # Dimensión de queries/keys/values
    seed=42            # Semilla para reproducibilidad
)
```

### AttentionClassifier (Original)

```python
model = AttentionClassifier(
    vocabulary,        # Objeto Vocabulary (requerido)
    embedding_dim=8,   # Dimensión de embeddings
    attention_dim=4,   # Dimensión de atención
    num_classes=8      # Número de clases (default: 8 para Well Intervention)
)
```

---

## Return Values

### EntityExtractor.extract()

```python
{
    'wells': [
        {'id': 'XX001', 'position': 8, 'confidence': 0.95},
        ...
    ],
    'events': [
        {'type': 'cañoneo', 'text': 'cañoneos', 'position': 20, 'confidence': 0.85},
        ...
    ],
    'dates': [
        {'type': 'year', 'year': 2020, 'text': '2020', 'position': 40, 'confidence': 0.85},
        ...
    ],
    'raw_text': 'Al pozo XX001 cuantos cañoneos ha tenido en el año 2020',
    'attention_scores': {...}  # Si se proporciona attention_weights
}
```

### QueryBuilder.build_query()

Retorna: `str` con query SQL

### QueryBuilder.get_mock_results()

Retorna: `List[Dict]` con registros simulados

```python
[
    {
        'well_id': 'XX001',
        'event_type': 'cañoneo',
        'event_date': '2020-03-15',
        'perforations_count': 24,
        'shot_depth': 3500,
        'shot_density': 2.5
    },
    ...
]
```

---

## Arquitectura de la Librería

```
mini_attention/
├── src/mini_attention/
│   ├── __init__.py                (exportaciones públicas)
│   │
│   ├── Well Intervention (NUEVO)
│   │   ├── entity_extractor.py    (extrae pozos, eventos, fechas)
│   │   ├── query_builder.py       (genera queries SQL)
│   │   └── well_dataset.py        (dataset de pozos)
│   │
│   ├── Core Attention
│   │   ├── attention.py           (Self-Attention)
│   │   ├── model.py               (AttentionClassifier pipeline)
│   │   ├── classifier.py          (clasificador lineal)
│   │   └── trainer.py             (entrenador)
│   │
│   ├── Data
│   │   ├── vocabulary.py          (vocabulario)
│   │   ├── tokenizer.py           (tokenizador)
│   │   ├── embeddings.py          (embeddings)
│   │   ├── dataset.py             (datasets base)
│   │   └── loss.py                (funciones de pérdida)
│   │
│   └── Utilities
│       ├── visualization.py       (gráficas de atención)
│       ├── math_utils.py          (utilidades matemáticas)
│
├── examples/
│   ├── well_intervention_example.py    (NUEVO - 5 ejemplos completos)
│   ├── basic_attention.py
│   ├── test_attention.py
│   ├── test_model.py
│   ├── train_model.py
│   ├── visualize_attention.py
│   └── compare_attention.py
│
├── README.md                    (este archivo)
├── pyproject.toml              (configuración del paquete)
└── .gitignore
```

---

## Conceptos Clave

### Self-Attention

Self-Attention permite que cada token en una secuencia **atienda a otros tokens**.

Fórmula:
```
Attention(Q, K, V) = softmax(Q · K^T / sqrt(d_k)) · V
```

Donde:
- `Q` (Query) = `X · W_Q`
- `K` (Key)   = `X · W_K`
- `V` (Value) = `X · W_V`
- `d_k` = dimensión de attention

### Entity Extraction

Extrae información estructurada de texto no estructurado:

1. **Tokenización**: Divide el texto en palabras
2. **Pattern Matching**: Identifica pozos, eventos, fechas usando regex
3. **Confidence Scoring**: Asigna confianza basada en tipo de patrón
4. **Attention Weighting** (opcional): Refina usando pesos de atención

### Query Generation

Transforma entidades en consultas SQL:

```
Entidades  →  Validación  →  SQL Generation  →  Query Result
Wells        Rules          WHERE clause       Database
Events       Mapping        SELECT clause      Results
Dates        Format         ORDER BY           Summary
```

---

## Notas de Desarrollo

- Los **embeddings permanecen congelados** durante entrenamiento
- Solo se entrenan los **pesos del clasificador**
- Implementación educativa, optimizada para **claridad** no rendimiento
- Requiere **NumPy** como única dependencia
- Entity extraction usa **regex** y **pattern matching** (no deep learning)
- Query generation es **determinístico** basado en entidades

---

## Casos de Uso

### 1. Asistente Conversacional para Pozos
```python
# El usuario pregunta en lenguaje natural
user_input = "Cuantos cañoneos en XX001 el 2020"

# El sistema responde automáticamente
entities = extractor.extract(user_input)
sql = builder.build_query(extractor.format_for_query(entities))
results = database.execute(sql)
```

### 2. Clasificación de Históricos
```python
# Clasificar registros históricos
for record in historical_records:
    event_class = model.forward(record['description'])
    # Guardar clasificación automáticamente
```

### 3. Búsqueda Inteligente
```python
# Búsqueda en base de datos usando lenguaje natural
query_results = builder.get_mock_results(entities)
# Retornar resultados relevantes al usuario
```

---

## Autor

Proyecto educativo de aprendizaje. Desarrollado para enseñar:
- Conceptos de Self-Attention
- Procesamiento de Lenguaje Natural
- Extracción de Entidades
- Generación de Queries SQL

## Licencia

MIT

---

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## Contacto

Para preguntas o sugerencias sobre el proyecto educativo, puedes crear un issue en el repositorio.
