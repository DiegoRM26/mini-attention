"""
Ejemplo completo de extracción de información sobre intervenciones en pozos.

Este ejemplo demuestra cómo:
1. Extraer entidades (pozos, eventos, fechas) de texto en lenguaje natural
2. Generar queries SQL para consultar la base de datos
3. Clasificar tipos de intervención
"""

import sys
from pathlib import Path

# Añadir el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mini_attention import (
    EntityExtractor,
    QueryBuilder,
    WellDatabase,
    WellInterventionDataset,
    Vocabulary,
    AttentionClassifier,
    Trainer
)


def print_results(results):
    """Imprime resultados simulados sea cual sea su forma (total/existe/filas)."""
    if not results:
        print("  (sin resultados)")
        return

    first = results[0]
    if "total" in first:
        print(f"  Total: {first['total']}")
    elif "existe" in first:
        print(f"  Existe: {'Si' if first['existe'] else 'No'}")
    else:
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['well_id']} - {result['event_type']} - {result['event_date']}")


def example_1_entity_extraction():
    """Ejemplo 1: Extracción básica de entidades."""
    print("=" * 70)
    print("EJEMPLO 1: Extracción de Entidades")
    print("=" * 70)

    extractor = EntityExtractor()

    queries = [
        "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020",
        "Cuantos areneos a tenido el pozo XX002 desde el año 2000 y 2010",
        "Que estimulación mecanica fue la ultima aplicada en el pozo XX003",
        "Dime si el Pozo CIRA001 tiene cañoneos en el año 2025",
    ]

    for query in queries:
        print(f"\nTexto: '{query}'")
        print("-" * 70)

        entities = extractor.extract(query)

        print(f"Pozos detectados: {entities['wells']}")
        print(f"Eventos detectados: {entities['events']}")
        print(f"Fechas detectadas: {entities['dates']}")
        print(f"Intención detectada: {entities['intent']}")

        # Formatear para query builder
        formatted = extractor.format_for_query(entities)
        print(f"\nFormato para query builder: {formatted}")


def example_2_query_generation():
    """Ejemplo 2: Generación de queries SQL."""
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Generación de Queries SQL")
    print("=" * 70)

    extractor = EntityExtractor()
    builder = QueryBuilder(db_type="postgresql")

    queries = [
        "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020",
        "Cuantos areneos a tenido el pozo XX002 desde el año 2000 y 2010",
        "Que estimulación mecanica fue la ultima aplicada en el pozo XX003",
        "Dime si el Pozo CIRA001 tiene cañoneos en el año 2025",
    ]

    for query in queries:
        print(f"\nPregunta: '{query}'")
        print("-" * 70)

        # Paso 1: Extraer entidades
        entities = extractor.extract(query)
        formatted = extractor.format_for_query(entities)

        # Paso 2: Generar query SQL
        sql = builder.build_query(formatted)
        print(f"Query SQL:\n{sql}")

        # Paso 3: Resumen en lenguaje natural
        summary = builder.get_summary(formatted)
        print(f"\nResumen: {summary}")

        # Paso 4: Resultados simulados (la forma depende de la intención)
        results = builder.get_mock_results(formatted)
        print("Resultados simulados:")
        print_results(results)


def example_3_event_classification():
    """Ejemplo 3: Clasificación de tipos de intervención."""
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Clasificación de Intervenciones")
    print("=" * 70)

    # Cargar dataset
    dataset = WellInterventionDataset()

    print(f"\nDataset de intervenciones en pozos:")
    print(f"  Total de ejemplos: {len(dataset)}")
    print(f"  Clases disponibles: {len(dataset.classes)}")

    # Mostrar estadísticas
    stats = dataset.get_statistics()
    print(f"\nEstadísticas del dataset:")
    print(f"  Ejemplos totales: {stats['total_examples']}")
    print(f"  Número de clases: {stats['num_classes']}")
    print(f"  Longitud promedio: {stats['avg_text_length']:.1f} palabras")

    print(f"\nDistribución de clases:")
    for class_name, count in stats["class_distribution"].items():
        print(f"  {class_name:30s}: {count:2d} ejemplos")

    # Mostrar ejemplos de cada clase
    print(f"\nEjemplos por clase:")
    for class_name in dataset.classes:
        examples = dataset.get_by_class(class_name)
        if examples:
            print(f"\n  {class_name}:")
            for ex in examples[:2]:  # Mostrar solo 2 ejemplos por clase
                print(f"    - {ex}")


def example_4_full_pipeline():
    """Ejemplo 4: Pipeline completo de extracción + clasificación."""
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Pipeline Completo")
    print("=" * 70)

    extractor = EntityExtractor()
    builder = QueryBuilder(db_type="postgresql")

    # Ejemplo de preguntas del usuario (incluye existencia, conteo, último y una ambigua)
    user_queries = [
        "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020",
        "Cuantos areneos a tenido el pozo XX002 desde el año 2000 y 2010",
        "Que estimulación mecanica fue la ultima aplicada en el pozo XX003",
        "XX001 cañoneos y areneos en 2020",
        "Historial completo de intervenciones en pozo XX002",
        "Dime si el Pozo CIRA001 tiene cañoneos en el año 2025",
    ]

    for i, user_query in enumerate(user_queries, 1):
        print(f"\n[Consulta {i}]")
        print(f"Usuario pregunta: '{user_query}'")
        print("-" * 70)

        # Extracción de entidades
        entities = extractor.extract(user_query)

        # Si faltara información clave (pozo o categoría), aquí es donde
        # el chat le preguntaría al usuario antes de seguir (ver example_6)
        clarification = extractor.needs_clarification(entities)
        if clarification:
            print(f"[Clarificación necesaria] {clarification['question']}")
            continue

        formatted = extractor.format_for_query(entities)

        # Información extraída
        print(f"Información extraída:")
        print(f"  Pozos: {formatted['wells']}")
        print(f"  Eventos: {formatted['event_types']}")
        print(f"  Fechas: {formatted['dates']}")
        print(f"  Intención: {formatted['intent']}")

        # Generar query
        sql = builder.build_query(formatted)
        summary = builder.get_summary(formatted)

        print(f"\nResumen: {summary}")
        print(f"\nQuery SQL generada:")
        for line in sql.split("\n"):
            print(f"  {line}")

        # Resultados simulados
        results = builder.get_mock_results(formatted)
        print("\nResultados:")
        print_results(results)


def example_5_attention_classification():
    """Ejemplo 5: Usar modelo de atención para clasificar intervenciones."""
    print("\n" + "=" * 70)
    print("EJEMPLO 5: Clasificación con Atención")
    print("=" * 70)

    # Preparar dataset
    dataset = WellInterventionDataset()
    vocab = Vocabulary()

    print(f"Vocabulario disponible: {vocab.size} palabras")

    # Crear modelo clasificador
    num_classes = len(dataset.classes)
    model = AttentionClassifier(
        vocabulary=vocab,
        embedding_dim=16,
        attention_dim=8,
        num_classes=num_classes
    )

    print(f"\nModelo de clasificación configurado:")
    print(f"  Clases disponibles: {num_classes}")
    print(f"  Dimensión de embeddings: 16")
    print(f"  Dimensión de atención: 8")

    # Demostración: Procesar ejemplos sin entrenamiento
    print(f"\nProcesando ejemplos del dataset (sin entrenamiento):")

    # Procesar algunos ejemplos
    for i in range(min(3, len(dataset))):
        text, _ = dataset[i]
        # Usar el modelo para procesar el texto y obtener pesos de atención
        result = model.forward(text, return_attention=True)
        predicted_class_id = result["prediction"]
        predicted_class = dataset.classes[predicted_class_id] if predicted_class_id < len(dataset.classes) else "unknown"
        actual_class = dataset.labels[i]

        print(f"\n  Texto: '{text}'")
        print(f"  Clase real: {actual_class}")
        print(f"  Predicción inicial: {predicted_class}")
        print(f"  Tokens procesados: {len(result['tokens'])}")


def example_6_clarification_flow():
    """Ejemplo 6: Flujo de clarificación cuando falta información clave."""
    print("\n" + "=" * 70)
    print("EJEMPLO 6: Flujo de Clarificación (preguntas de seguimiento)")
    print("=" * 70)

    extractor = EntityExtractor()
    builder = QueryBuilder()

    casos = [
        {
            "pregunta": "¿El pozo XX005 tuvo alguna intervención en 2021?",
            "respuesta_usuario": "Cañoneos",
        },
        {
            "pregunta": "¿Cuántas intervenciones hubo en total durante 2020?",
            "respuesta_usuario": "XX001, cañoneos",
        },
    ]

    for caso in casos:
        pregunta = caso["pregunta"]
        respuesta = caso["respuesta_usuario"]

        print(f"\nUsuario: '{pregunta}'")

        entities = extractor.extract(pregunta)
        clarification = extractor.needs_clarification(entities)

        if not clarification:
            print("  (no se necesitó clarificación)")
            continue

        print(f"Asistente: {clarification['question']}")
        if clarification.get("options"):
            print(f"  Opciones rápidas: {clarification['options']}")

        print(f"Usuario: '{respuesta}'")

        # Se combina la pregunta original con la respuesta de clarificación
        # y se vuelve a extraer sobre el texto combinado (sin volver a preguntar).
        combined_text = f"{pregunta} {respuesta}"
        final_entities = extractor.extract(combined_text)
        formatted = extractor.format_for_query(final_entities)

        sql = builder.build_query(formatted)
        summary = builder.get_summary(formatted)
        results = builder.get_mock_results(formatted)

        print(f"\nResumen final: {summary}")
        print(f"Query SQL generada:")
        for line in sql.split("\n"):
            print(f"  {line}")
        print("Resultados:")
        print_results(results)


def example_7_real_dataset():
    """Ejemplo 7: Ejecutar las queries generadas contra un dataset real (SQLite)."""
    print("\n" + "=" * 70)
    print("EJEMPLO 7: Consultar un Dataset Real")
    print("=" * 70)

    # Base de datos de ejemplo en memoria, sembrada de forma reproducible
    db = WellDatabase(db_path=":memory:", seed=42)
    print(f"\nDataset cargado: {db.total_records()} eventos en {len(db.list_wells())} pozos")
    print(f"Pozos disponibles: {db.list_wells()}")

    extractor = EntityExtractor()
    builder = QueryBuilder()

    preguntas = [
        "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020",
        "Que estimulación mecanica fue la ultima aplicada en el pozo XX003",
        "Dime si el Pozo CIRA001 tiene cañoneos en el año 2025",
    ]

    for query in preguntas:
        entities = extractor.extract(query)
        formatted = extractor.format_for_query(entities)
        sql = builder.build_query(formatted)

        print(f"\nPregunta: '{query}'")
        print(f"Query SQL:\n{sql}")

        # A diferencia de get_mock_results(), esto ejecuta la query de verdad
        rows = db.execute(sql)

        # Y esto redacta la respuesta en lenguaje natural a partir del resultado real
        answer = builder.build_answer(formatted, rows)
        print(f"Respuesta: {answer}")

    # También se puede explorar un pozo directamente sin pasar por lenguaje natural
    print("\nHistorial completo de XX001 (vía WellDatabase.get_well_summary):")
    for row in db.get_well_summary("XX001")[:5]:
        print(f"  {row['event_date']} | {row['event_type']:20s} | {row['description']}")


def main():
    """Ejecuta todos los ejemplos."""
    print("\n")
    print("=" * 70)
    print("  LIBRARY: Extracción de Información en Pozos Petroleros")
    print("  Usando Self-Attention para NLP")
    print("=" * 70)

    try:
        example_1_entity_extraction()
        example_2_query_generation()
        example_3_event_classification()
        example_4_full_pipeline()
        example_5_attention_classification()
        example_6_clarification_flow()
        example_7_real_dataset()

        print("\n" + "=" * 70)
        print("[SUCCESS] Todos los ejemplos completados exitosamente")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n[ERROR] Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
