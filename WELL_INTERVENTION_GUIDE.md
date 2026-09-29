# Guía: Extracción de Información en Pozos Petroleros

Esta guía detalla cómo usar el módulo de extracción de entidades y generación de queries para intervenciones en pozos petroleros.

---

## Tabla de Contenidos

1. [Inicio Rápido](#inicio-rápido)
2. [EntityExtractor](#entityextractor)
3. [QueryBuilder](#querybuilder)
4. [Dataset de Pozos](#dataset-de-pozos)
5. [Pipeline Completo](#pipeline-completo)
6. [Patrones Soportados](#patrones-soportados)
7. [Casos de Uso](#casos-de-uso)
8. [Troubleshooting](#troubleshooting)

---

## Inicio Rápido

```python
from mini_attention import EntityExtractor, QueryBuilder

# 1. Crear extractor
extractor = EntityExtractor()

# 2. Extraer entidades de una pregunta
texto = "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020"
entities = extractor.extract(texto)

# 3. Formatear para query builder
formatted = extractor.format_for_query(entities)

# 4. Crear builder y generar query
builder = QueryBuilder()
sql = builder.build_query(formatted)

# 5. Obtener resumen en lenguaje natural
summary = builder.get_summary(formatted)
print(summary)  # "Query busca: pozos XX001 | Eventos: cañoneo | Año: 2020"

# 6. Obtener resultados simulados
results = builder.get_mock_results(formatted)
for result in results:
    print(f"Pozo {result['well_id']}: {result['event_type']} el {result['event_date']}")
```

---

## EntityExtractor

### Propósito

Extrae información estructurada (entidades) de texto en lenguaje natural no estructurado.

### Inicialización

```python
from mini_attention import EntityExtractor

extractor = EntityExtractor()
```

No requiere configuración adicional. Usa patrones regex predefinidos.

### Métodos Principales

#### 1. `extract(text, attention_weights=None)`

Extrae todas las entidades de un texto.

**Parámetros:**
- `text` (str): Texto de entrada en lenguaje natural
- `attention_weights` (np.ndarray, opcional): Matriz de pesos de atención para mejorar confianza

**Retorna:**
```python
{
    'wells': [
        {
            'id': 'XX001',           # ID del pozo
            'position': 8,           # Posición en el texto
            'confidence': 0.95       # Confianza de extracción (0-1)
        }
    ],
    'events': [
        {
            'type': 'cañoneo',       # Tipo de evento
            'text': 'cañoneos',      # Texto encontrado
            'position': 20,          # Posición en el texto
            'confidence': 0.85       # Confianza
        }
    ],
    'dates': [
        {
            'type': 'year',          # Tipo de fecha
            'year': 2020,            # Año
            'text': '2020',          # Texto encontrado
            'position': 40,          # Posición en el texto
            'confidence': 0.85       # Confianza
        }
    ],
    'raw_text': '...',                # Texto original
    'attention_scores': {...}         # Si se proporciona attention_weights
}
```

**Ejemplos:**

```python
# Ejemplo 1: Extracción simple
entities = extractor.extract("Pozo XX001 cañoneos 2020")
print(entities['wells'])    # [{'id': 'XX001', ...}]
print(entities['events'])   # [{'type': 'cañoneo', ...}]
print(entities['dates'])    # [{'type': 'year', 'year': 2020}]

# Ejemplo 2: Múltiples pozos y eventos
entities = extractor.extract(
    "Pozos XX001 y XX002: cañoneos y areneos en 2020 y 2021"
)
print(len(entities['wells']))   # 2
print(len(entities['events']))  # 2
print(len(entities['dates']))   # 2

# Ejemplo 3: Rango de fechas
entities = extractor.extract(
    "Intervenciones en pozo XX003 desde 2000 hasta 2010"
)
date = entities['dates'][0]
print(date['type'])        # 'year_range'
print(date['start'])       # 2000
print(date['end'])         # 2010
```

#### 2. `format_for_query(entities)`

Formatea entidades para uso con QueryBuilder.

**Parámetros:**
- `entities` (dict): Resultado de `extract()`

**Retorna:**
```python
{
    'wells': ['XX001', 'XX002'],           # Lista de IDs de pozos
    'event_types': ['cañoneo', 'araneo'],  # Lista de tipos de eventos
    'dates': {                             # Información de fechas
        'start': 2000,                     # Para rangos
        'end': 2010
    }
    # O para años simples:
    # 'dates': {'year': 2020}
}
```

**Ejemplo:**

```python
entities = extractor.extract("XX001 cañoneos 2020")
formatted = extractor.format_for_query(entities)
print(formatted)
# {
#   'wells': ['XX001'],
#   'event_types': ['cañoneo'],
#   'dates': {'year': 2020}
# }
```

### Patrones Soportados

#### Pozos
- `pozo XX001` → detecta "XX001"
- `XX001` → detecta "XX001"
- `well XX001` → detecta "XX001"

#### Eventos
- Cañoneos: "cañoneos", "disparos", "shooting"
- Areneos: "areneos", "sandeo", "arena"
- Estimulación: "estimulación mecánica", "fractura hidráulica"
- Limpieza: "limpieza", "cleaning", "lavado"
- Perforación: "perforación", "drilling"
- Revestimiento: "revestimiento", "casing", "tubing"

#### Fechas
- Años: "2020", "1995"
- Rangos: "2000 a 2010", "2000-2010", "2000 hasta 2010"
- Períodos: "desde 2000 hasta 2010"

---

## QueryBuilder

### Propósito

Genera queries SQL y resúmenes en lenguaje natural basados en entidades extraídas.

### Inicialización

```python
from mini_attention import QueryBuilder

# Para PostgreSQL (default)
builder = QueryBuilder(db_type="postgresql")

# Para otras bases de datos
builder = QueryBuilder(db_type="mysql")
builder = QueryBuilder(db_type="sqlite")
```

### Métodos Principales

#### 1. `build_query(entities)`

Genera una query SQL basada en entidades.

**Parámetros:**
- `entities` (dict): Diccionario formateado por `format_for_query()`

**Retorna:**
- `str`: Query SQL

**Ejemplo:**

```python
from mini_attention import EntityExtractor, QueryBuilder

extractor = EntityExtractor()
builder = QueryBuilder()

text = "Cañoneos en pozo XX001 año 2020"
entities = extractor.extract(text)
formatted = extractor.format_for_query(entities)

sql = builder.build_query(formatted)
print(sql)
# SELECT 
#     well_id,
#     event_type,
#     event_date,
#     perforations_count, shot_depth, shot_density
# FROM well_perforations
# WHERE well_id IN ('XX001')
#   AND YEAR(event_date) = 2020
# ORDER BY event_date DESC;
```

#### 2. `get_summary(entities)`

Retorna un resumen en lenguaje natural de la query.

**Parámetros:**
- `entities` (dict): Diccionario formateado por `format_for_query()`

**Retorna:**
- `str`: Resumen en lenguaje natural

**Ejemplo:**

```python
formatted = {
    'wells': ['XX001'],
    'event_types': ['cañoneo'],
    'dates': {'year': 2020}
}

summary = builder.get_summary(formatted)
print(summary)
# Output: "Query busca: pozos XX001 | Eventos: cañoneo | Año: 2020"
```

#### 3. `get_mock_results(entities)`

Retorna resultados simulados para demostración.

**Parámetros:**
- `entities` (dict): Diccionario formateado por `format_for_query()`

**Retorna:**
- `List[Dict]`: Lista de registros simulados

**Ejemplo:**

```python
results = builder.get_mock_results(formatted)
# [
#   {
#     'well_id': 'XX001',
#     'event_type': 'cañoneo',
#     'event_date': '2020-03-15',
#     'perforations_count': 24,
#     'shot_depth': 3500,
#     'shot_density': 2.5
#   }
# ]

# Usar resultados
for result in results:
    print(f"{result['well_id']}: {result['event_type']} el {result['event_date']}")
```

---

## Dataset de Pozos

### WellInterventionDataset

Dataset con 25+ ejemplos de intervenciones en pozos.

#### Inicialización

```python
from mini_attention import WellInterventionDataset

dataset = WellInterventionDataset()
```

#### Propiedades

```python
# Número de ejemplos
len(dataset)  # 25

# Clases disponibles
dataset.classes  # ['perforations', 'cleaning', 'stimulation', ...]

# Acceder a ejemplos
text, label_id = dataset[0]

# Obtener ejemplos por clase
perforations = dataset.get_by_class("perforations")

# Estadísticas
stats = dataset.get_statistics()
# {
#   'total_examples': 25,
#   'num_classes': 8,
#   'avg_text_length': 7.2,
#   'class_distribution': {
#     'perforations': 5,
#     'cleaning': 5,
#     ...
#   }
# }
```

#### Clases Disponibles

| Clase | Descripción | Ejemplos |
|-------|-------------|----------|
| `perforations` | Cañoneos/disparos | 5 |
| `cleaning` | Areneos/limpieza | 5 |
| `stimulation` | Estimulación mecánica | 5 |
| `casing` | Revestimiento | 1 |
| `drilling` | Perforación | 1 |
| `maintenance` | Mantenimiento | 1 |
| `repair` | Reparación | 1 |
| `combined` | Operaciones combinadas | 3 |

---

## Pipeline Completo

### Flujo End-to-End

```
Pregunta en Lenguaje Natural
           ↓
    EntityExtractor.extract()
           ↓
   EntityExtractor.format_for_query()
           ↓
    QueryBuilder.build_query()
           ↓
     SQL Query + Summary
           ↓
   Database Execution (mock)
           ↓
    Resultados + Visualización
```

### Código Completo

```python
from mini_attention import EntityExtractor, QueryBuilder

# 1. Entrada del usuario
user_query = "Pozo XX001: cuantos cañoneos y areneos desde 2010 hasta 2020"

# 2. Extraer entidades
extractor = EntityExtractor()
entities = extractor.extract(user_query)

# 3. Validar extracción
if not entities['wells']:
    print("No se encontraron pozos")
else:
    print(f"Pozos encontrados: {[w['id'] for w in entities['wells']]}")

# 4. Formatear para query builder
formatted = extractor.format_for_query(entities)

# 5. Generar query
builder = QueryBuilder()
sql = builder.build_query(formatted)
print("Query generada:")
print(sql)

# 6. Obtener resumen
summary = builder.get_summary(formatted)
print(f"\nResumen: {summary}")

# 7. Simular resultados
results = builder.get_mock_results(formatted)
print(f"\nResultados encontrados: {len(results)} registros")

# 8. Mostrar resultados
for result in results:
    print(f"  • {result['well_id']}: {result['event_type']} ({result['event_date']})")
```

---

## Patrones Soportados

### Pozos (Well IDs)

Formato: Letras (0-2) + Números (3-5)

**Patrones:**
- `XX001`, `XX002`, `AB123` ✓
- `X001`, `ABC001` ✓
- `1234` (solo números) ✗

**Ejemplos válidos:**
```python
extractor.extract("Pozo XX001")         # ✓
extractor.extract("XX001")              # ✓
extractor.extract("well XX001")         # ✓
extractor.extract("XX001 cañoneos")     # ✓
extractor.extract("Pozos XX001 XX002")  # ✓ (detecta ambos)
```

### Eventos

**Cañoneos:**
- "cañoneo", "cañoneos", "disparos", "shooting"

**Areneos:**
- "araneo", "areneos", "sandeo", "arena"

**Estimulación:**
- "estimulación mecánica", "fractura hidráulica", "frac job"

**Limpieza:**
- "limpieza", "cleaning", "lavado"

**Perforación:**
- "perforación", "perforación", "drilling"

**Revestimiento:**
- "revestimiento", "casing", "tubing"

### Fechas

**Años simples:**
```python
extractor.extract("en el año 2020")      # ✓ 2020
extractor.extract("2020")                 # ✓ 2020
extractor.extract("durante 1995")         # ✓ 1995
```

**Rangos de años:**
```python
extractor.extract("desde 2000 hasta 2010")     # ✓ start=2000, end=2010
extractor.extract("2000 a 2010")               # ✓ start=2000, end=2010
extractor.extract("2000-2010")                 # ✓ start=2000, end=2010
```

---

## Casos de Uso

### Caso 1: Búsqueda Simple

**Entrada:**
```
"Cañoneos en pozo XX001"
```

**Salida:**
```python
{
    'wells': ['XX001'],
    'event_types': ['cañoneo'],
    'dates': None
}

SQL: SELECT * FROM well_events 
     WHERE well_id IN ('XX001') 
     AND event_type = 'cañoneo'
```

### Caso 2: Búsqueda con Fechas

**Entrada:**
```
"Areneos en XX002 durante 2020"
```

**Salida:**
```python
{
    'wells': ['XX002'],
    'event_types': ['araneo'],
    'dates': {'year': 2020}
}

SQL: SELECT * FROM well_events 
     WHERE well_id IN ('XX002') 
     AND event_type = 'araneo'
     AND YEAR(event_date) = 2020
```

### Caso 3: Búsqueda Compleja

**Entrada:**
```
"Intervenciones en XX001 y XX002: cañoneos y estimulación desde 2010 a 2020"
```

**Salida:**
```python
{
    'wells': ['XX001', 'XX002'],
    'event_types': ['cañoneo', 'estimulación_mecánica'],
    'dates': {'start': 2010, 'end': 2020}
}

SQL: SELECT * FROM well_events
     WHERE well_id IN ('XX001', 'XX002')
     AND event_type IN ('cañoneo', 'estimulación_mecánica')
     AND event_date BETWEEN '2010-01-01' AND '2020-12-31'
```

---

## Troubleshooting

### Problema: No se detectan pozos

**Causa:** El formato del pozo no coincide con el patrón esperado.

**Solución:**
- Usa formato `LETRALETRA + NUMEROS`
- Ejemplos válidos: `XX001`, `AB123`, `X001`
- Asegúrate de que el ID esté separado por espacios

```python
# ✓ Funciona
extractor.extract("pozo XX001")

# ✗ No funciona (sin espacios)
extractor.extract("pozo:XX001")  # No detecta
```

### Problema: No se detectan eventos

**Causa:** El tipo de evento no está en los patrones predefinidos.

**Solución:**
- Verifica que uses términos reconocidos
- Puedes ver patrones en `EntityExtractor.EVENT_PATTERNS`

```python
# ✓ Funciona
extractor.extract("cañoneos realizados")

# ✗ No funciona (término no reconocido)
extractor.extract("operación de perforación especial")
```

### Problema: Extrae fechas incorrectamente

**Causa:** El patrón de fecha no coincide con el texto.

**Solución:**
- Usa formatos estándar: "AÑO", "AÑO a AÑO", "desde AÑO hasta AÑO"

```python
# ✓ Funciona
extractor.extract("en 2020")
extractor.extract("de 2000 a 2010")

# ✗ No funciona
extractor.extract("20xx")      # Formato no válido
extractor.extract("2020 al 2025")  # Usa "hasta" en lugar de "al"
```

### Problema: QueryBuilder retorna query muy general

**Causa:** No se extrajeron suficientes entidades.

**Solución:**
- Verifica que la pregunta tenga pozos O eventos
- Incluye más detalles en la pregunta

```python
# ✓ Funciona
extractor.extract("XX001 cañoneos")

# ✗ Retorna query genérica
extractor.extract("operaciones")  # Sin pozo ni evento específico
```

---

## Extensiones Posibles

### 1. Agregar nuevos tipos de eventos

Edita `EntityExtractor.EVENT_PATTERNS`:

```python
class EntityExtractor:
    EVENT_PATTERNS = {
        ...
        "nuevo_evento": [
            r"patrón1",
            r"patrón2",
        ]
    }
```

### 2. Agregar nuevas tablas de base de datos

Edita `QueryBuilder.table_mappings`:

```python
class QueryBuilder:
    def __init__(self):
        self.table_mappings = {
            ...
            "nuevo_evento": "tabla_evento",
        }
```

### 3. Personalizar campos de query

Edita `QueryBuilder._get_event_fields()`:

```python
def _get_event_fields(self, event_type: str) -> str:
    fields = {
        ...
        "nuevo_evento": "campo1, campo2, campo3",
    }
```

---

## Integración con Bases de Datos Reales

Para usar con una base de datos real, reemplaza `get_mock_results()`:

```python
import psycopg2

def execute_real_query(sql, db_config):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return results

# Uso
from mini_attention import EntityExtractor, QueryBuilder

extractor = EntityExtractor()
builder = QueryBuilder()

entities = extractor.extract("Pozo XX001 cañoneos 2020")
formatted = extractor.format_for_query(entities)
sql = builder.build_query(formatted)

# Ejecutar en base de datos real
db_config = {
    'host': 'localhost',
    'database': 'wells_db',
    'user': 'username',
    'password': 'password'
}
results = execute_real_query(sql, db_config)
```

---

## Más Información

- Vea `examples/well_intervention_example.py` para más ejemplos
- Consulte `README.md` para arquitectura general
- Revise el código fuente de `entity_extractor.py` y `query_builder.py`
