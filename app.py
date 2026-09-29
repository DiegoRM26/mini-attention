"""
App de Chat en Streamlit para consultas de intervenciones en pozos petroleros.

El usuario escribe una pregunta en lenguaje natural y la app:
1. Extrae entidades (pozos, eventos, fechas, intención) con EntityExtractor
2. Si falta información clave (p.ej. la categoría del evento), pregunta
   al usuario para clarificar antes de construir la query
3. Genera una Query SQL con QueryBuilder
4. Ejecuta esa query contra un dataset real (SQLite, generado por
   WellDatabase) y muestra los resultados obtenidos
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mini_attention import EntityExtractor, QueryBuilder, WellDatabase


st.set_page_config(
    page_title="Asistente de Pozos Petroleros",
    page_icon="🛢️",
    layout="centered",
)

INTENT_LABELS = {
    "count": "Conteo (¿cuántos?)",
    "last": "Último registro",
    "existence": "Verificación de existencia (¿tiene / hubo?)",
    "list": "Listado / historial completo",
}

# Ejemplos agrupados por intención, para mostrar la variedad de preguntas soportadas.
EXAMPLES_BY_GROUP = {
    "Verificar existencia": [
        "Dime si el Pozo CIRA001 tiene cañoneos en el año 2025",
        "¿El pozo AB1234 tuvo areneos entre 2015 y 2020?",
        "¿Hubo estimulación mecánica en el pozo XX003 en 2019?",
    ],
    "Contar": [
        "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020",
        "Cuantos areneos a tenido el pozo XX002 desde el año 2000 y 2010",
        "¿Cuántas limpiezas tuvo el pozo XX004 en 2021?",
    ],
    "Último registro": [
        "Que estimulación mecanica fue la ultima aplicada en el pozo XX003",
        "¿Cuál fue el último cañoneo del pozo XX001?",
    ],
    "Historial completo": [
        "XX001 cañoneos y areneos en 2020",
        "Historial completo de intervenciones en pozo XX002",
    ],
    "Preguntas ambiguas (activan clarificación)": [
        "¿El pozo XX005 tuvo alguna intervención en 2021?",
        "¿Cuántas intervenciones hubo en total durante 2020?",
    ],
}


@st.cache_resource
def get_pipeline(db_type: str):
    extractor = EntityExtractor()
    builder = QueryBuilder(db_type=db_type)
    return extractor, builder


@st.cache_resource
def get_database():
    """Base de datos de ejemplo (SQLite) contra la que se ejecutan las queries."""
    return WellDatabase(seed=42)


def format_entities_markdown(entities: dict) -> str:
    wells = [w["id"] for w in entities["wells"] if w["id"]]
    events = [e["type"] for e in entities["events"]]
    dates = entities["dates"]
    intent = entities.get("intent", "list")

    lines = []
    lines.append(f"**Pozos:** {', '.join(wells) if wells else '_ninguno detectado_'}")
    lines.append(f"**Eventos:** {', '.join(events) if events else '_ninguno detectado_'}")

    if dates:
        date_strs = []
        for d in dates:
            if d["type"] == "year_range":
                date_strs.append(f"{d['start']}–{d['end']}")
            elif d["type"] == "year":
                date_strs.append(str(d["year"]))
        lines.append(f"**Fechas:** {', '.join(date_strs)}")
    else:
        lines.append("**Fechas:** _ninguna detectada_")

    lines.append(f"**Intención detectada:** {INTENT_LABELS.get(intent, intent)}")

    return "\n\n".join(lines)


def run_query(sql: str, formatted: dict, db: WellDatabase, builder: QueryBuilder) -> tuple[list, bool]:
    """
    Ejecuta la query contra el dataset real. Si por algún motivo la
    ejecución falla (p.ej. una combinación de entidades no contemplada),
    recurre a resultados simulados como red de seguridad para la demo.
    """
    try:
        return db.execute(sql), True
    except Exception:
        return builder.get_mock_results(formatted), False


def render_assistant_response(response: dict, builder: QueryBuilder) -> str:
    """Construye el contenido markdown de la respuesta final del asistente."""
    parts = []

    source_note = "" if response.get("from_db", True) else " _(query no ejecutable, usando datos simulados)_"
    answer = builder.build_answer(response["formatted"], response["results"])
    parts.append(f"**Respuesta:** {answer}{source_note}")

    parts.append(f"**Interpretación:** {response['summary']}")
    parts.append("**Entidades detectadas:**\n\n" + format_entities_markdown(response["entities"]))
    parts.append(f"**Query SQL generada:**\n```sql\n{response['sql']}\n```")

    results = response["results"]
    if results and "total" not in results[0] and "existe" not in results[0]:
        parts.append(f"**Detalle de los {len(results)} registro(s):**")
        for r in results:
            campos = ", ".join(
                f"{k}: {v}" for k, v in r.items() if k not in ("well_id", "event_type", "event_date")
            )
            parts.append(f"- **{r['well_id']}** | {r['event_type']} | {r['event_date']} | {campos}")

    return "\n\n".join(parts)


def render_clarification_message(clarification: dict) -> str:
    content = f"🤔 {clarification['question']}"
    if clarification.get("options"):
        content += "\n\n_Elige una opción abajo o escribe tu respuesta._"
    return content


def handle_user_turn(user_text: str, extractor: EntityExtractor, builder: QueryBuilder, db: WellDatabase) -> str:
    """
    Procesa un turno del usuario: si había una clarificación pendiente,
    combina la respuesta con la pregunta original y resuelve la query
    definitiva (sin volver a preguntar). Si no, extrae entidades de cero
    y decide si hace falta pedir más información.
    """
    pending = st.session_state.get("pending_clarification")

    if pending:
        combined_text = f"{pending['original_text']} {user_text}"
        st.session_state["pending_clarification"] = None
        entities = extractor.extract(combined_text)
        clarification = None  # ya se preguntó una vez: se resuelve con lo que haya
    else:
        entities = extractor.extract(user_text)
        clarification = extractor.needs_clarification(entities)

    if clarification:
        st.session_state["pending_clarification"] = {
            "original_text": user_text,
            "clarification": clarification,
        }
        return render_clarification_message(clarification)

    formatted = extractor.format_for_query(entities)
    sql = builder.build_query(formatted)
    summary = builder.get_summary(formatted)
    results, from_db = run_query(sql, formatted, db, builder)

    return render_assistant_response({
        "entities": entities,
        "formatted": formatted,
        "sql": sql,
        "summary": summary,
        "results": results,
        "from_db": from_db,
    }, builder)


def main():
    st.title("🛢️ Asistente de Intervenciones en Pozos")
    st.caption(
        "Escribe una pregunta en lenguaje natural sobre intervenciones en pozos "
        "(cañoneos, areneos, estimulación mecánica, etc.). El asistente extrae pozo, "
        "evento y fechas, y si le falta información te preguntará antes de generar la Query SQL."
    )

    db = get_database()

    with st.sidebar:
        st.header("Configuración")
        db_type = st.selectbox("Motor de base de datos", ["postgresql", "mysql", "sqlite"], index=0)
        st.caption(
            "Solo cambia la sintaxis mostrada en la Query SQL; la ejecución "
            "real siempre corre contra el dataset SQLite de ejemplo."
        )

        st.markdown("---")
        st.subheader("📊 Dataset disponible")
        wells = db.list_wells()
        st.caption(f"{db.total_records()} eventos registrados en {len(wells)} pozos")
        selected_well = st.selectbox("Explorar pozo", wells)
        if selected_well:
            summary = db.get_well_summary(selected_well)
            st.dataframe(
                [{"Evento": r["event_type"], "Fecha": r["event_date"], "Detalle": r["description"]} for r in summary],
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("---")
        st.subheader("Ejemplos de preguntas")
        for group_name, ejemplos in EXAMPLES_BY_GROUP.items():
            with st.expander(group_name, expanded=False):
                for ej in ejemplos:
                    if st.button(ej, use_container_width=True, key=f"ej_{hash(ej)}"):
                        st.session_state["pending_input"] = ej
                        st.rerun()

        st.markdown("---")
        if st.button("🗑️ Limpiar conversación", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["pending_clarification"] = None
            st.rerun()

    extractor, builder = get_pipeline(db_type)

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "pending_clarification" not in st.session_state:
        st.session_state["pending_clarification"] = None

    # Mostrar historial de la conversación
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Si hay una clarificación pendiente con opciones, mostrar botones rápidos
    pending = st.session_state["pending_clarification"]
    if pending and pending["clarification"].get("options"):
        st.caption("Elige una opción rápida:")
        options = pending["clarification"]["options"]
        cols = st.columns(2)
        for i, opt in enumerate(options):
            if cols[i % 2].button(opt, key=f"clarify_opt_{i}_{hash(opt)}", use_container_width=True):
                st.session_state["pending_input"] = opt
                st.rerun()

    # Input: prioriza click en ejemplo/opción rápida, si no usa chat_input
    pending_input = st.session_state.pop("pending_input", None)
    user_text = st.chat_input("Escribe tu consulta sobre pozos...") or pending_input

    if user_text:
        st.session_state["messages"].append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        with st.chat_message("assistant"):
            with st.spinner("Analizando consulta..."):
                content = handle_user_turn(user_text, extractor, builder, db)
            st.markdown(content)

        st.session_state["messages"].append({"role": "assistant", "content": content})
        st.rerun()


if __name__ == "__main__":
    main()
