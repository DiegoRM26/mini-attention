# Changelog: Módulo de Intervenciones en Pozos Petroleros

## Versión 2.0 - Módulo de Extracción de Entidades para Pozos Petroleros

### Nuevas Características

#### 1. **EntityExtractor** (`entity_extractor.py`)
Extrator de entidades para lenguaje natural en intervenciones de pozos:
- Detección de **IDs de pozos** (XX001, AB123, etc.)
- Detección de **tipos de eventos** (cañoneos, areneos, estimulación mecánica, etc.)
- Detección de **fechas** (años simples y rangos)
- Cálculo de **confianza** para cada entidad
- Integración opcional con **pesos de atención**

**Patrones soportados:**
- Pozos: `XX001`, `A001`, `XYZ123`
- Eventos: cañoneo, araneo, estimulación_mecánica, limpieza, perforación, revestimiento
- Fechas: `2020`, `2000 a 2010`, `desde 2000 hasta 2010`

#### 2. **QueryBuilder** (`query_builder.py`)
Constructor automático de queries SQL basado en entidades extraídas:
- Generación automática de **queries SELECT**
- Mapeo de eventos a **tablas de base de datos**
- Soporte para **PostgreSQL, MySQL, SQLite**
- Generación de **resúmenes en lenguaje natural**
- Retorno de **resultados simulados** para demostración

**Ejemplo de uso:**
```python
extractor = EntityExtractor()
builder = QueryBuilder(db_type="postgresql")

entities = extractor.extract("Pozo XX001 cañoneos 2020")
formatted = extractor.format_for_query(entities)
sql = builder.build_query(formatted)
```

#### 3. **WellInterventionDataset** (`well_dataset.py`)
Dataset especializado con 24+ ejemplos de intervenciones en pozos:
- **8 clases** de intervenciones
- Textos en **lenguaje natural español**
- Métodos para acceder a ejemplos por clase
- **Estadísticas** del dataset
- **Data loader** para batches

#### 4. **Documentación**
- `README.md` - Actualizado con nueva funcionalidad
- `WELL_INTERVENTION_GUIDE.md` - Guía detallada de uso
- `CHANGELOG.md` - Este archivo

### Ejemplos Completos

#### `examples/well_intervention_example.py`
5 ejemplos ejecutables:
1. **Extracción de Entidades** - Cómo extraer pozos, eventos y fechas
2. **Generación de Queries SQL** - Cómo construir queries automáticamente
3. **Clasificación de Intervenciones** - Estadísticas del dataset
4. **Pipeline Completo** - End-to-end de extracción → query
5. **Clasificación con Atención** - Uso del modelo de atención

### Modificaciones a Archivos Existentes

#### `__init__.py`
- Agregadas exportaciones para `EntityExtractor`, `QueryBuilder`, `WellInterventionDataset`, `WellDataLoader`

#### `entity_extractor.py` (Nueva)
- Patrones regex para pozos, eventos y fechas
- Métodos de extracción con scoring de confianza
- Formateo para query builder
- Análisis de pesos de atención

#### `query_builder.py` (Nueva)
- Mapeo de eventos a tablas
- Generación de queries SELECT/WHERE/ORDER BY
- Resúmenes en lenguaje natural
- Resultados simulados

#### `well_dataset.py` (Nueva)
- Dataset de 24 ejemplos clasificados
- 8 clases de intervención
- Métodos estadísticos
- Data loader para entrenamiento

### Casos de Uso

#### 1. Asistente Conversacional
```python
# El usuario pregunta en lenguaje natural
user_input = "Cuantos cañoneos en XX001 el 2020"

# Sistema extrae entidades y genera query
entities = extractor.extract(user_input)
sql = builder.build_query(extractor.format_for_query(entities))
results = database.execute(sql)
```

#### 2. Clasificación Automática
```python
dataset = WellInterventionDataset()
for record in historical_records:
    text_class = dataset.classes[model.predict(record['text'])]
```

#### 3. Búsqueda Inteligente
```python
results = builder.get_mock_results(formatted_entities)
# Retornar resultados relevantes al usuario
```

### Tipos de Intervención Soportados

| Clase | Descripción | Ejemplos |
|-------|-------------|----------|
| `perforations` | Cañoneos/disparos | 5 |
| `cleaning` | Areneos/limpieza | 5 |
| `stimulation` | Estimulación mecánica | 5 |
| `combined` | Operaciones combinadas | 5 |
| `casing` | Revestimiento | 1 |
| `drilling` | Perforación | 1 |
| `maintenance` | Mantenimiento | 1 |
| `repair` | Reparación | 1 |

### Compatibilidad

- ✓ Python 3.8+
- ✓ NumPy (dependencia existente)
- ✓ Windows, macOS, Linux
- ✓ Compatible con código existente (backward compatible)

### Ejemplos de Preguntas Soportadas

**Simples:**
- "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020"
- "Cuantos areneos a tenido el pozo XX002"
- "Estimulación mecánica en XX003"

**Complejas:**
- "XX001 cañoneos y areneos en 2020"
- "Pozo XX002 intervenciones desde 2000 hasta 2022"
- "Historial completo de intervenciones"

### Instalación

```bash
# Instalar la librería con el nuevo módulo
pip install -e .

# Ejecutar ejemplo completo
python examples/well_intervention_example.py
```

### Estructura del Proyecto (Actualizada)

```
mini_attention/
├── src/mini_attention/
│   ├── __init__.py
│   ├── entity_extractor.py       ← NUEVO
│   ├── query_builder.py          ← NUEVO
│   ├── well_dataset.py           ← NUEVO
│   ├── attention.py
│   ├── model.py
│   ├── classifier.py
│   ├── trainer.py
│   ├── vocabulary.py
│   ├── tokenizer.py
│   ├── embeddings.py
│   ├── dataset.py
│   ├── loss.py
│   ├── math_utils.py
│   └── visualization.py
│
├── examples/
│   ├── well_intervention_example.py  ← NUEVO (5 ejemplos)
│   ├── basic_attention.py
│   ├── test_attention.py
│   └── ...
│
├── README.md                  ← ACTUALIZADO
├── WELL_INTERVENTION_GUIDE.md ← NUEVO
├── CHANGELOG.md              ← ESTE ARCHIVO
└── pyproject.toml
```

### Próximas Mejoras Posibles

1. **Entrenamiento del modelo de atención** para mejorar clasificación
2. **Soporte para más tipos de eventos** específicos del dominio
3. **Integración con bases de datos reales** (PostgreSQL, MySQL)
4. **Interfaz web** para demostración interactiva
5. **API REST** para uso en aplicaciones
6. **Validación de entidades** contra reglas de negocio
7. **Logging y auditoría** de queries ejecutadas
8. **Manejo de errores** más robusto
9. **Testing** completo
10. **Documentación en inglés**

### Notas de Desarrollo

- Implementación educativa, enfocada en claridad
- Usa regex para extracción (no requiere modelos complejos)
- Queries SQL son **determinísticas** basadas en entidades
- Totalmente **compatible** con el código existente
- Sin dependencias adicionales (solo NumPy)

### Testing

Para verificar que todo funciona:

```bash
# Ejecutar ejemplo completo
python examples/well_intervention_example.py

# Ejecutar ejemplos originales
python examples/basic_attention.py
python examples/train_model.py
```

### Contribuciones

Las mejoras y contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -m 'Agregar caracteristica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

---

## Historial de Cambios Detallado

### Archivos Creados
- ✓ `src/mini_attention/entity_extractor.py` - 243 líneas
- ✓ `src/mini_attention/query_builder.py` - 182 líneas
- ✓ `src/mini_attention/well_dataset.py` - 143 líneas
- ✓ `examples/well_intervention_example.py` - 295 líneas
- ✓ `WELL_INTERVENTION_GUIDE.md` - Guía completa
- ✓ `CHANGELOG.md` - Este archivo

### Archivos Modificados
- ✓ `src/mini_attention/__init__.py` - Agregadas exportaciones
- ✓ `README.md` - Actualizado con nueva funcionalidad

### Total de Líneas Agregadas
- **863 líneas** de código nuevo
- **3000+ líneas** de documentación

---

**Fecha de Última Actualización:** 2026-09-21
**Versión:** 2.0.0
**Estado:** Producción (Educativo)
