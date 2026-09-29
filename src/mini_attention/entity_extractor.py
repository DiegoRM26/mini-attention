import re
import numpy as np
from typing import Dict, List, Optional


class EntityExtractor:
    """
    Extractor de entidades para intervenciones en pozos petroleros.
    Utiliza patrones regex y análisis de atención para identificar:
    - Nombres/IDs de pozos
    - Tipos de eventos (cañoneos, areneos, estimulación mecánica, etc.)
    - Fechas involucradas (años, períodos)
    - Intención de la pregunta (existencia, conteo, último, historial)
    """

    # Patrones de eventos petroleros
    EVENT_PATTERNS = {
        "cañoneo": [
            r"cañone[os]?",
            r"disparo[s]?",
            r"shooting",
        ],
        "araneo": [
            r"ar[ae]ne[oa]s?",       # areneo(s) / araneo(s) (variantes regionales)
            r"sandeo[s]?",
            r"arena(?:miento|do)?s?",
        ],
        "estimulación_mecánica": [
            r"estimulaci[óo]n\s+mec[áa]nica",
            r"estimulaci[óo]n(?:es)?\s+mecanic\w*",
            r"fractura.*hidr[áa]ulica",
            r"frac.*job",
            r"mechanical.*stimulation",
        ],
        "limpieza": [
            r"limpieza[s]?",
            r"cleaning",
            r"lavado[s]?",
        ],
        "perforación": [
            r"perforaci[óo]n\s+(?:del|de|completa)",
            r"drilling",
        ],
        "revestimiento": [
            r"revestimiento[s]?",
            r"casing",
            r"tubing",
        ],
    }

    # Nombres legibles para cada categoría de evento
    CATEGORY_OPTIONS = [
        ("cañoneo", "Cañoneos"),
        ("araneo", "Areneos"),
        ("estimulación_mecánica", "Estimulación mecánica"),
        ("limpieza", "Limpieza"),
        ("perforación", "Perforación"),
        ("revestimiento", "Revestimiento"),
    ]

    ALL_EVENTS_LABEL = "Todos los eventos"

    # Patrones para pozos: 1 a 5 letras seguidas de 2 a 6 dígitos
    # (soporta IDs cortos como "X001" y largos como "CIRA001")
    _WELL_ID = r"[A-Z]{1,5}\d{2,6}"
    WELL_PATTERNS = [
        rf"pozo\s+({_WELL_ID})",   # pozo XX001 / pozo CIRA001
        rf"well\s+({_WELL_ID})",   # well XX001
        rf"\b({_WELL_ID})\b",      # XX001 directo
    ]

    # Patrones para fechas
    _YEAR = r"(?:19|20)\d{2}"
    DATE_PATTERNS = {
        "year": rf"\b{_YEAR}\b",
        # Cubre: "2000 a 2010", "2000-2010", "2000 hasta 2010", "2000 y 2010",
        # y variantes con prefijos como "desde", "entre", "el año" que se ignoran.
        "year_range": rf"\b({_YEAR})\s*(?:a|hasta|-|y)\s*({_YEAR})\b",
    }

    # Patrones de intención de la pregunta (orden de prioridad: primero el que matchee gana)
    INTENT_PATTERNS = {
        "count": r"\b(cu[áa]nt[oa]s|cantidad\s+de)\b",
        "last": r"\b([úu]ltim[oa]s?|m[áa]s\s+reciente)\b",
        "list": r"\b(historial|listado|lista\s+de|todas\s+las|todos\s+los|resumen\s+de)\b",
        "existence": r"\b(tiene|tuvo|hay|existe|dime\s+si|verificar\s+si|se\s+realiz[óo]|se\s+ha\s+realizado|hubo)\b",
    }
    INTENT_ORDER = ["count", "last", "list", "existence"]
    DEFAULT_INTENT = "list"

    def __init__(self):
        self.well_pattern = re.compile("|".join(self.WELL_PATTERNS), re.IGNORECASE)
        self.event_patterns = {}
        for event_type, patterns in self.EVENT_PATTERNS.items():
            self.event_patterns[event_type] = re.compile("|".join(patterns), re.IGNORECASE)
        self.date_patterns = {k: re.compile(v, re.IGNORECASE) for k, v in self.DATE_PATTERNS.items()}
        self.intent_patterns = {k: re.compile(v, re.IGNORECASE) for k, v in self.INTENT_PATTERNS.items()}

    def extract(self, text: str, attention_weights: Optional[np.ndarray] = None) -> Dict:
        """
        Extrae entidades del texto usando patrones y pesos de atención.

        Args:
            text: Texto de entrada en lenguaje natural
            attention_weights: Pesos de atención opcionales (n_tokens, n_tokens)

        Returns:
            Diccionario con entidades extraídas y confianza
        """
        entities = {
            "wells": self._extract_wells(text),
            "events": self._extract_events(text),
            "dates": self._extract_dates(text),
            "intent": self._extract_intent(text),
            "raw_text": text,
        }

        # Si hay pesos de atención, usarlos para mejorar la confianza
        if attention_weights is not None:
            entities["attention_scores"] = self._compute_attention_scores(
                text, attention_weights
            )

        return entities

    def _extract_wells(self, text: str) -> List[Dict]:
        """Extrae nombres/IDs de pozos del texto."""
        wells = []
        seen = set()

        for match in self.well_pattern.finditer(text):
            # Cada alternativa del patrón tiene su propio grupo numerado;
            # match.lastindex apunta al grupo que realmente participó.
            well_id = match.group(match.lastindex) if match.lastindex else match.group(0)
            if not well_id:
                continue
            well_id = well_id.upper()
            if well_id not in seen:
                wells.append({
                    "id": well_id,
                    "position": match.start(),
                    "confidence": 0.95,  # Patrón muy confiable
                })
                seen.add(well_id)

        return wells

    def _extract_events(self, text: str) -> List[Dict]:
        """Extrae tipos de eventos del texto."""
        events = []
        seen = set()

        for event_type, pattern in self.event_patterns.items():
            for match in pattern.finditer(text):
                event_key = f"{event_type}_{match.start()}"
                if event_key not in seen:
                    events.append({
                        "type": event_type,
                        "text": match.group(0),
                        "position": match.start(),
                        "confidence": 0.85,
                    })
                    seen.add(event_key)

        return sorted(events, key=lambda x: x["position"])

    def _extract_dates(self, text: str) -> List[Dict]:
        """Extrae fechas/períodos del texto."""
        dates = []

        # Rangos de años (incluye "desde X y Y", "entre X y Y", "X hasta Y", "X-Y")
        for match in self.date_patterns["year_range"].finditer(text):
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            if start_year > end_year:
                start_year, end_year = end_year, start_year
            dates.append({
                "type": "year_range",
                "start": start_year,
                "end": end_year,
                "text": match.group(0),
                "position": match.start(),
                "confidence": 0.9,
            })

        # Años simples
        for match in self.date_patterns["year"].finditer(text):
            year = int(match.group(0))
            # Evitar contar años que ya fueron parte de un rango
            skip = False
            for d in dates:
                if d["type"] == "year_range" and d["start"] <= year <= d["end"]:
                    skip = True
                    break
            if not skip:
                dates.append({
                    "type": "year",
                    "year": year,
                    "text": match.group(0),
                    "position": match.start(),
                    "confidence": 0.85,
                })

        return sorted(dates, key=lambda x: x["position"])

    def _extract_intent(self, text: str) -> str:
        """
        Detecta la intención de la pregunta: count, last, list o existence.
        Se evalúa en un orden de prioridad fijo porque una misma frase puede
        contener varias palabras clave (p.ej. "cuántos... tiene...").
        """
        for intent in self.INTENT_ORDER:
            if self.intent_patterns[intent].search(text):
                return intent
        return self.DEFAULT_INTENT

    def _compute_attention_scores(
        self,
        text: str,
        attention_weights: np.ndarray
    ) -> Dict:
        """
        Usa pesos de atención para mejorar confianza de entidades.

        Args:
            text: Texto tokenizado
            attention_weights: Matriz de pesos de atención

        Returns:
            Diccionario con scores de atención
        """
        return {
            "mean_attention": float(np.mean(attention_weights)),
            "max_attention": float(np.max(attention_weights)),
            "attention_entropy": float(self._entropy(attention_weights.mean(axis=0))),
        }

    @staticmethod
    def _entropy(probabilities: np.ndarray) -> float:
        """Calcula entropía de una distribución de probabilidad."""
        p = probabilities[probabilities > 0]
        return -float(np.sum(p * np.log(p)))

    def format_for_query(self, entities: Dict) -> Dict:
        """
        Formatea las entidades extraídas para generar queries.

        Returns:
            Diccionario con formato optimizado para query builder
        """
        formatted = {
            "wells": [e["id"] for e in entities["wells"] if e["id"] is not None],
            "event_types": list(set(e["type"] for e in entities["events"])),
            "dates": None,
            "intent": entities.get("intent", self.DEFAULT_INTENT),
        }

        # Procesar fechas (se usa el primer bloque de fecha detectado)
        if entities["dates"]:
            date_info = entities["dates"][0]
            if date_info["type"] == "year_range":
                formatted["dates"] = {
                    "start": date_info["start"],
                    "end": date_info["end"],
                }
            elif date_info["type"] == "year":
                formatted["dates"] = {"year": date_info["year"]}

        return formatted

    def needs_clarification(self, entities: Dict) -> Optional[Dict]:
        """
        Determina si falta información clave para construir una query con
        sentido y, de ser así, devuelve una pregunta de clarificación para
        hacerle al usuario (con opciones rápidas cuando aplica).

        Reglas:
        1. Si no se detectó ni pozo ni categoría de evento, se pide ambos
           datos en texto libre (no hay botones posibles para el pozo).
        2. Si se detectó pozo pero no categoría, y la intención de la
           pregunta no es un listado genérico ("historial"/"todas"), se
           pregunta la categoría con botones de opción rápida.

        Returns:
            None si no hace falta preguntar nada, o un dict con
            {"type", "question", "options"(opcional)}.
        """
        wells = [w["id"] for w in entities["wells"] if w["id"]]
        events = entities["events"]
        intent = entities.get("intent", self.DEFAULT_INTENT)

        if not wells and not events:
            return {
                "type": "missing_well_and_category",
                "question": (
                    "No logré identificar el pozo ni el tipo de evento. "
                    "¿Podrías indicarme el número de pozo (ej. XX001) y la "
                    "categoría de intervención (cañoneos, areneos, estimulación "
                    "mecánica, limpieza, perforación o revestimiento)?"
                ),
            }

        if not events and intent != "list":
            well_txt = f" para el pozo {', '.join(wells)}" if wells else ""
            options = [label for _, label in self.CATEGORY_OPTIONS] + [self.ALL_EVENTS_LABEL]
            return {
                "type": "missing_category",
                "question": f"¿A qué tipo de intervención te refieres{well_txt}?",
                "options": options,
            }

        return None

    def resolve_category_label(self, label: str) -> Optional[str]:
        """Convierte una etiqueta legible (p.ej. 'Cañoneos') a su tipo interno."""
        normalized = label.strip().lower()
        for key, readable in self.CATEGORY_OPTIONS:
            if readable.lower() == normalized:
                return key
        return None
