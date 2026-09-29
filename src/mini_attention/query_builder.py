from typing import Dict, List, Optional, Any


class QueryBuilder:
    """
    Constructor de queries SQL para intervenciones en pozos petroleros.
    Genera queries basadas en entidades extraídas (pozos, eventos, fechas)
    y en la intención de la pregunta (existencia, conteo, último registro
    o listado/historial completo).
    """

    INTENT_LABELS = {
        "count": "Contar",
        "existence": "Verificar existencia de",
        "last": "Buscar el último registro de",
        "list": "Listar",
    }

    # (singular, plural, es_femenino) legible por tipo de evento, para redactar la respuesta
    EVENT_LABELS = {
        "cañoneo": ("cañoneo", "cañoneos", False),
        "araneo": ("areneo", "areneos", False),
        "estimulación_mecánica": ("estimulación mecánica", "estimulaciones mecánicas", True),
        "limpieza": ("limpieza", "limpiezas", True),
        "perforación": ("perforación", "perforaciones", True),
        "revestimiento": ("revestimiento", "revestimientos", False),
    }

    def __init__(self, db_type: str = "postgresql"):
        """
        Args:
            db_type: Tipo de base de datos ('postgresql', 'mysql', 'sqlite', etc.)
        """
        self.db_type = db_type
        self.table_mappings = {
            "cañoneo": "well_perforations",
            "araneo": "well_cleaning",
            "estimulación_mecánica": "well_stimulation",
            "limpieza": "well_cleaning",
            "perforación": "well_drilling",
            "revestimiento": "well_casing",
        }

    def build_query(self, entities: Dict[str, Any]) -> str:
        """
        Construye una query SQL basada en entidades extraídas y la
        intención detectada (count / existence / last / list).

        Args:
            entities: Diccionario con wells, event_types, dates, intent

        Returns:
            Query SQL como string
        """
        wells = entities.get("wells", [])
        event_types = entities.get("event_types", [])
        dates = entities.get("dates", {})
        intent = entities.get("intent", "list")

        if not wells and not event_types:
            return self._build_default_query()

        table, fields = self._resolve_table_and_fields(event_types)
        where_clauses = self._build_where_clauses(wells, event_types, dates)

        if intent == "count":
            select_clause = "SELECT COUNT(*) AS total"
            tail = ""
        elif intent == "existence":
            select_clause = "SELECT COUNT(*) > 0 AS existe"
            tail = ""
        elif intent == "last":
            select_clause = f"SELECT\n    well_id,\n    event_type,\n    event_date,\n    {fields}"
            tail = "\nORDER BY event_date DESC\nLIMIT 1"
        else:  # "list" / historial completo
            select_clause = f"SELECT\n    well_id,\n    event_type,\n    event_date,\n    {fields}"
            tail = "\nORDER BY event_date DESC"

        sql = f"{select_clause}\nFROM {table}"
        if where_clauses:
            sql += "\nWHERE " + "\n  AND ".join(where_clauses)
        sql += tail + ";"

        return sql

    def _resolve_table_and_fields(self, event_types: List[str]) -> (str, str):
        """Determina la tabla y los campos según los tipos de evento pedidos."""
        if not event_types:
            return "well_events", "description, details"
        if len(event_types) == 1:
            event_type = event_types[0]
            table = self.table_mappings.get(event_type, "well_events")
            return table, self._get_event_fields(event_type)
        # Múltiples categorías a la vez: se consulta la tabla genérica
        return "well_events", "description, details"

    def _build_where_clauses(
        self,
        wells: List[str],
        event_types: List[str],
        dates: Optional[Dict]
    ) -> List[str]:
        """Construye la lista de condiciones para la cláusula WHERE."""
        clauses = []

        if wells:
            clauses.append(f"well_id IN ({self._format_list(wells)})")

        if event_types:
            if len(event_types) == 1:
                clauses.append(f"event_type = '{event_types[0]}'")
            else:
                clauses.append(f"event_type IN ({self._format_list(event_types)})")

        if dates:
            if "start" in dates and "end" in dates:
                clauses.append(
                    f"event_date BETWEEN '{dates['start']}-01-01' AND '{dates['end']}-12-31'"
                )
            elif "year" in dates:
                clauses.append(f"YEAR(event_date) = {dates['year']}")

        return clauses

    def _build_default_query(self) -> str:
        """Query por defecto si no hay entidades claras."""
        return """
SELECT
    well_id,
    event_type,
    event_date,
    description
FROM well_events
ORDER BY event_date DESC
LIMIT 100;
""".strip()

    def _get_event_fields(self, event_type: str) -> str:
        """Retorna campos específicos según tipo de evento."""
        fields = {
            "cañoneo": "perforations_count, shot_depth, shot_density",
            "araneo": "cleaning_type, volume_removed",
            "estimulación_mecánica": "fluid_volume, prop_mass, injection_rate",
            # Comparte tabla (well_cleaning) y por lo tanto columnas con "araneo"
            "limpieza": "cleaning_type, volume_removed",
            "perforación": "depth, diameter, duration_hours",
            "revestimiento": "diameter, grade, connection_type",
        }
        return fields.get(event_type, "details")

    def _format_list(self, items: List[str]) -> str:
        """Formatea lista para usar en SQL IN clause."""
        return ", ".join([f"'{item}'" for item in items])

    def get_summary(self, entities: Dict[str, Any]) -> str:
        """
        Retorna un resumen en lenguaje natural de la query.

        Args:
            entities: Diccionario con entidades extraídas

        Returns:
            Descripción en lenguaje natural de la query
        """
        wells = entities.get("wells", [])
        event_types = entities.get("event_types", [])
        dates = entities.get("dates", {})
        intent = entities.get("intent", "list")

        action = self.INTENT_LABELS.get(intent, "Listar")
        summary = f"{action}: "

        if wells:
            summary += f"pozos {', '.join(wells)}"
        else:
            summary += "todos los pozos"

        if event_types:
            summary += f" | Eventos: {', '.join(event_types)}"
        else:
            summary += " | Eventos: todos"

        if dates:
            if "start" in dates and "end" in dates:
                summary += f" | Período: {dates['start']} - {dates['end']}"
            elif "year" in dates:
                summary += f" | Año: {dates['year']}"

        return summary

    def get_mock_results(self, entities: Dict[str, Any]) -> List[Dict]:
        """
        Retorna resultados de ejemplo para demostración, adaptados a la
        intención de la pregunta:
        - "count"     -> [{"total": N}]
        - "existence" -> [{"existe": True/False}]
        - "last"      -> solo el registro más reciente
        - "list"      -> todos los registros simulados

        Args:
            entities: Diccionario con entidades extraídas

        Returns:
            Lista de resultados simulados
        """
        intent = entities.get("intent", "list")
        base_results = self._generate_base_results(entities)

        if intent == "count":
            return [{"total": len(base_results)}]
        if intent == "existence":
            return [{"existe": len(base_results) > 0}]
        if intent == "last":
            return base_results[:1]
        return base_results

    def _generate_base_results(self, entities: Dict[str, Any]) -> List[Dict]:
        """Genera las filas simuladas antes de aplicar el recorte por intención."""
        wells = entities.get("wells") or ["XX001", "XX002"]
        event_types = entities.get("event_types", [])

        catalog = {
            "cañoneo": {
                "event_date": "2020-03-15",
                "perforations_count": 24,
                "shot_depth": 3500,
                "shot_density": 2.5,
            },
            "araneo": {
                "event_date": "2020-06-20",
                "cleaning_type": "arena",
                "volume_removed": 450,
            },
            "estimulación_mecánica": {
                "event_date": "2020-09-10",
                "fluid_volume": 5000,
                "prop_mass": 450000,
                "injection_rate": 50,
            },
            "limpieza": {
                "event_date": "2021-11-05",
                "cleaning_type": "general",
                "volume_removed": 200,
            },
        }

        types_to_use = event_types if event_types else list(catalog.keys())

        results = []
        for well_id in wells:
            for event_type in types_to_use:
                data = catalog.get(event_type)
                if data is None:
                    continue
                results.append({
                    "well_id": well_id,
                    "event_type": event_type,
                    **data,
                })

        return results

    def build_answer(self, entities: Dict[str, Any], results: List[Dict]) -> str:
        """
        Redacta en español la respuesta a la pregunta original a partir de
        los resultados reales obtenidos (de WellDatabase o del fallback
        simulado), en vez de mostrar solo los datos crudos.

        Args:
            entities: Diccionario formateado (wells, event_types, dates, intent)
            results: Filas devueltas por la ejecución de la query

        Returns:
            Respuesta en lenguaje natural
        """
        wells = entities.get("wells", [])
        event_types = entities.get("event_types", [])
        dates = entities.get("dates", {})
        intent = entities.get("intent", "list")

        wells_phrase, plural = self._wells_phrase(wells)
        date_phrase = self._date_phrase(dates)

        if intent == "count":
            total = results[0]["total"] if results else 0
            verb = "tienen" if plural else "tiene"
            event_phrase = self._event_phrase(event_types, total)
            wells_phrase_cap = wells_phrase[0].upper() + wells_phrase[1:]
            return f"{wells_phrase_cap} {verb} {total} {event_phrase}{date_phrase}."

        if intent == "existence":
            existe = bool(results[0]["existe"]) if results else False
            verb = "registran" if plural else "registra"
            event_phrase = self._event_phrase(event_types)
            if existe:
                return f"Sí, {wells_phrase} {verb} {event_phrase}{date_phrase}."
            return f"No, {wells_phrase} no {verb} {event_phrase}{date_phrase}."

        if intent == "last":
            if not results:
                event_phrase = self._event_phrase(event_types)
                return f"No se encontraron registros de {event_phrase} para {wells_phrase}{date_phrase}."
            return self._describe_last(wells_phrase, results[0])

        # "list" / historial completo
        if not results:
            event_phrase = self._event_phrase(event_types)
            return f"No se encontraron registros de {event_phrase} para {wells_phrase}{date_phrase}."
        n = len(results)
        registro_word = "registro" if n == 1 else "registros"
        verbo = "encontró" if n == 1 else "encontraron"
        return f"Se {verbo} {n} {registro_word} para {wells_phrase}{date_phrase}."

    def _wells_phrase(self, wells: List[str]):
        """Devuelve (frase, es_plural) para referirse a los pozos consultados."""
        if not wells:
            return "todos los pozos", True
        if len(wells) == 1:
            return f"el pozo {wells[0]}", False
        return f"los pozos {', '.join(wells)}", True

    def _date_phrase(self, dates: Optional[Dict]) -> str:
        """Frase temporal a anexar a la respuesta (con espacio inicial), o ''."""
        if not dates:
            return ""
        if "start" in dates and "end" in dates:
            return f" entre {dates['start']} y {dates['end']}"
        if "year" in dates:
            return f" en el año {dates['year']}"
        return ""

    def _event_phrase(self, event_types: List[str], count: Optional[int] = None) -> str:
        """Frase legible para uno o varios tipos de evento, con concordancia numérica."""
        if not event_types:
            return "intervenciones" if count != 1 else "intervención"

        labels = []
        for event_type in event_types:
            singular, plural, _ = self.EVENT_LABELS.get(event_type, (event_type, event_type, False))
            labels.append(singular if count == 1 else plural)
        return " y ".join(labels)

    def _describe_last(self, wells_phrase: str, row: Dict[str, Any]) -> str:
        """Redacta la descripción del registro más reciente según sus columnas."""
        event_type = row.get("event_type")
        date = row.get("event_date")
        label, _, feminine = self.EVENT_LABELS.get(event_type, (event_type or "evento", None, False))
        articulo, adjetivo = ("La última", "registrada") if feminine else ("El último", "registrado")

        if "perforations_count" in row:
            detail = (
                f"{row['perforations_count']} disparos a {row['shot_depth']} m de profundidad "
                f"(densidad {row['shot_density']})"
            )
        elif "cleaning_type" in row:
            detail = f"tipo {row['cleaning_type']}, con {row['volume_removed']} unidades removidas"
        elif "fluid_volume" in row:
            detail = (
                f"volumen de fluido {row['fluid_volume']}, masa de apuntalante {row['prop_mass']}, "
                f"tasa de inyección {row['injection_rate']}"
            )
        elif "depth" in row and "duration_hours" in row:
            detail = f"profundidad {row['depth']} m, diámetro {row['diameter']}, duración {row['duration_hours']} horas"
        elif "grade" in row:
            detail = f"grado {row['grade']}, diámetro {row['diameter']}, conexión {row['connection_type']}"
        elif "description" in row:
            detail = row["description"]
        else:
            detail = None

        base = f"{articulo} {label} {adjetivo} en {wells_phrase} fue el {date}"
        return f"{base}, con {detail}." if detail else f"{base}."
