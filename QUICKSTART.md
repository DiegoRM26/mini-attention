# Quick Start: Extracción de Información en Pozos Petroleros

Comienza en 5 minutos con el módulo de extracción de entidades para intervenciones en pozos.

---

## 1. Instalación (30 segundos)

```bash
cd C:\Users\Diego\Documents\Ejercicios\mini_attention
pip install -e .
```

---

## 2. Ejemplo Mínimo (1 minuto)

```python
from mini_attention import EntityExtractor, QueryBuilder

# Crear extractores
extractor = EntityExtractor()
builder = QueryBuilder()

# Pregunta en lenguaje natural
pregunta = "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020"

# 1. Extraer entidades
entities = extractor.extract(pregunta)
print("Pozos:", [w["id"] for w in entities["wells"]])
print("Eventos:", [e["type"] for e in entities["events"]])
print("Fechas:", [d.get("year", d) for d in entities["dates"]])

# 2. Formatear para query builder
formatted = extractor.format_for_query(entities)

# 3. Generar SQL automáticamente
sql = builder.build_query(formatted)
print("\nSQL generado:")
print(sql)

# 4. Obtener resumen
summary = builder.get_summary(formatted)
print("\nResumen:", summary)

# 5. Resultados simulados
results = builder.get_mock_results(formatted)
print("\nResultados:")
for r in results:
    print(f"  {r['well_id']} - {r['event_type']} - {r['event_date']}")
```

**Salida esperada:**
```
Pozos: ['XX001']
Eventos: ['cañoneo']
Fechas: [2020]

SQL generado:
SELECT 
    well_id,
    event_type,
    event_date,
    perforations_count, shot_depth, shot_density
FROM well_perforations
WHERE well_id IN ('XX001')
  AND YEAR(event_date) = 2020
ORDER BY event_date DESC;

Resumen: Query busca: pozos XX001 | Eventos: cañoneo | Año: 2020

Resultados:
  XX001 - cañoneo - 2020-03-15
```

---

## 3. Ejemplos Listos (2 minutos)

```bash
# Ejecutar ejemplo completo con 5 demostraciones
python examples/well_intervention_example.py
```

**Incluye:**
1. Extracción de entidades de 3 preguntas
2. Generación de queries SQL
3. Estadísticas del dataset de pozos
4. Pipeline completo de 5 consultas
5. Clasificación con modelo de atención

---

## 4. Casos de Uso Comunes

### 4.1 Clasificar tipo de intervención

```python
from mini_attention import WellInterventionDataset

dataset = WellInterventionDataset()

# Ver clases disponibles
print("Tipos de intervención:")
for cls in dataset.classes:
    print(f"  - {cls}")

# Ver ejemplos de cada clase
print("\nEjemplos de 'perforations':")
for ex in dataset.get_by_class("perforations"):
    print(f"  - {ex}")
```

### 4.2 Buscar en múltiples pozos

```python
extractor = EntityExtractor()
builder = QueryBuilder()

# Pregunta con múltiples pozos
pregunta = "Pozos XX001 y XX002: cañoneos y areneos en 2020"

entities = extractor.extract(pregunta)
formatted = extractor.format_for_query(entities)
sql = builder.build_query(formatted)

print(sql)
# Genera query con WHERE ... IN ('XX001', 'XX002') y múltiples eventos
```

### 4.3 Rango de fechas

```python
pregunta = "Intervenciones en XX003 desde 2000 hasta 2020"

entities = extractor.extract(pregunta)
formatted = extractor.format_for_query(entities)
sql = builder.build_query(formatted)

print(sql)
# Genera query con BETWEEN '2000-01-01' AND '2020-12-31'
```

### 4.4 Procesamiento por lotes

```python
preguntas = [
    "Cañoneos en XX001",
    "Limpieza en XX002",
    "Estimulación en XX003",
]

extractor = EntityExtractor()
builder = QueryBuilder()

for pregunta in preguntas:
    entities = extractor.extract(pregunta)
    formatted = extractor.format_for_query(entities)
    
    summary = builder.get_summary(formatted)
    results = builder.get_mock_results(formatted)
    
    print(f"{pregunta}")
    print(f"  → {summary}")
    print(f"  → {len(results)} resultados\n")
```

---

## 5. Patrones Que Funciona

### Pozos
```python
# Todos estos funcionan:
extractor.extract("pozo XX001")       # Con "pozo"
extractor.extract("XX001")             # Solo el ID
extractor.extract("well XX001")        # En inglés
extractor.extract("Pozos XX001 XX002") # Múltiples
```

### Eventos
```python
# Todos estos funcionan:
extractor.extract("cañoneos")              # Cañoneos
extractor.extract("areneos")               # Areneos
extractor.extract("estimulación mecánica") # Estimulación
extractor.extract("limpieza")              # Limpieza
extractor.extract("perforación")           # Perforación
extractor.extract("revestimiento")         # Revestimiento
```

### Fechas
```python
# Todos estos funcionan:
extractor.extract("2020")           # Año simple
extractor.extract("2000 a 2010")    # Rango con "a"
extractor.extract("2000-2010")      # Rango con "-"
extractor.extract("desde 2000 hasta 2010")  # Explícito
```

---

## 6. Patrones Que NO Funciona

```python
# Estos NO funcionan (pero podemos agregar soporte):
extractor.extract("1234")          # Solo números, sin letras
extractor.extract("XY1")           # Muy pocas cifras
extractor.extract("2020s")         # Año con sufijo

# Soluciones:
extractor.extract("XX001")         # Agrega letras
extractor.extract("XX002")         # O usa otro ID
extractor.extract("el año 2020")   # Sé explícito
```

---

## 7. Integración con Base de Datos Real

Para usar con una BD real en lugar de resultados simulados:

```python
import psycopg2

def execute_query(sql, db_config):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return results

# Uso
from mini_attention import EntityExtractor, QueryBuilder

extractor = EntityExtractor()
builder = QueryBuilder(db_type="postgresql")

db_config = {
    'host': 'localhost',
    'database': 'wells_db',
    'user': 'username',
    'password': 'password'
}

pregunta = "Pozo XX001 cañoneos 2020"
entities = extractor.extract(pregunta)
formatted = extractor.format_for_query(entities)
sql = builder.build_query(formatted)

# Ejecutar en BD real
results = execute_query(sql, db_config)
for row in results:
    print(row)
```

---

## 8. Métodos Principales

### EntityExtractor

```python
extractor = EntityExtractor()

# Extraer todas las entidades
entities = extractor.extract("Pozo XX001 cañoneos 2020")

# Acceder a resultados
wells = entities["wells"]       # Lista de pozos con confianza
events = entities["events"]     # Lista de eventos
dates = entities["dates"]       # Lista de fechas

# Formatear para query builder
formatted = extractor.format_for_query(entities)
# {'wells': ['XX001'], 'event_types': ['cañoneo'], 'dates': {'year': 2020}}
```

### QueryBuilder

```python
builder = QueryBuilder(db_type="postgresql")

# Generar SQL
sql = builder.build_query(formatted)

# Obtener resumen legible
summary = builder.get_summary(formatted)
# "Query busca: pozos XX001 | Eventos: cañoneo | Año: 2020"

# Obtener resultados simulados
results = builder.get_mock_results(formatted)
# [{'well_id': 'XX001', 'event_type': 'cañoneo', ...}]
```

### WellInterventionDataset

```python
dataset = WellInterventionDataset()

# Acceder a datos
text, label_id = dataset[0]

# Acceder a ejemplos por clase
perforations = dataset.get_by_class("perforations")

# Estadísticas
stats = dataset.get_statistics()
print(stats["class_distribution"])
```

---

## 9. Troubleshooting

### Error: `No se detectan pozos`
**Solución:** Usa formato `LETRA(S) + NÚMEROS`, ej: `XX001`

### Error: `No se detectan eventos`
**Solución:** Verifica que uses términos reconocidos (cañoneo, araneo, etc.)

### Error: `Resultados simulados vacíos`
**Solución:** Normal si los parámetros no coinciden con datos. Usa `get_mock_results()` para generar resultados.

### Error de encoding en Windows
**Solución:** Asegúrate de ejecutar en PowerShell o cmd con UTF-8

---

## 10. Próximos Pasos

1. **Lee la guía completa:** `WELL_INTERVENTION_GUIDE.md`
2. **Explora ejemplos avanzados:** `examples/well_intervention_example.py`
3. **Personaliza patrones:** Edita `entity_extractor.py`
4. **Integra con tu BD:** Usa el método en sección 7
5. **Contribuye:** Agrega más tipos de eventos

---

## Resumen

| Tarea | Comando/Código | Documentación |
|-------|---|---|
| Instalar | `pip install -e .` | README.md |
| Ejemplo mínimo | Ver arriba | Quick Start |
| Ejemplos completos | `python examples/well_intervention_example.py` | Sección 3 |
| Guía detallada | `WELL_INTERVENTION_GUIDE.md` | Completa |
| API Reference | Ver código fuente | entity_extractor.py, query_builder.py |

---

**¡Listo para empezar!** 🚀

Ejecuta:
```bash
python examples/well_intervention_example.py
```

O prueba el ejemplo mínimo en la sección 2.
