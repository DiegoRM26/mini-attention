import pytest


def test_extracts_well_event_year(extractor):
    e = extractor.extract("Al pozo XX001 cuantos cañoneos ha tenido en el año 2020")
    assert [w["id"] for w in e["wells"]] == ["XX001"]
    assert [ev["type"] for ev in e["events"]] == ["cañoneo"]
    assert e["dates"][0]["year"] == 2020
    assert e["intent"] == "count"


def test_year_range(extractor):
    e = extractor.extract("Cuantos areneos a tenido el pozo XX002 desde el año 2000 y 2010")
    assert (e["dates"][0]["start"], e["dates"][0]["end"]) == (2000, 2010)


@pytest.mark.parametrize("text,intent", [
    ("Dime si el Pozo CIRA001 tiene cañoneos en el año 2025", "existence"),
    ("Que estimulación mecanica fue la ultima aplicada en el pozo XX003", "last"),
    ("Historial completo de intervenciones en pozo XX002", "list"),
])
def test_intents(extractor, text, intent):
    assert extractor.extract(text)["intent"] == intent


def test_clarification_when_category_missing(extractor):
    e = extractor.extract("¿El pozo XX005 tuvo alguna intervención en 2021?")
    q = extractor.needs_clarification(e)
    assert q and q["type"] == "missing_category" and q["options"]


def test_no_clarification_when_complete(extractor):
    e = extractor.extract("XX001 cañoneos y areneos en 2020")
    assert extractor.needs_clarification(e) is None


def test_sql_targets_right_table(extractor, builder):
    f = extractor.format_for_query(extractor.extract("pozo XX001 cañoneos 2020"))
    sql = builder.build_query(f)
    assert "well_perforations" in sql and "XX001" in sql and "2020" in sql


def test_end_to_end_against_database(extractor, builder, db):
    q = "Al pozo XX001 cuantos cañoneos ha tenido en el año 2020"
    f = extractor.format_for_query(extractor.extract(q))
    rows = db.execute(builder.build_query(f))
    assert rows[0]["total"] >= 0
    assert "XX001" in builder.build_answer(f, rows)


def test_last_event_query(extractor, builder, db):
    q = "Que estimulación mecanica fue la ultima aplicada en el pozo XX003"
    f = extractor.format_for_query(extractor.extract(q))
    rows = db.execute(builder.build_query(f))
    assert len(rows) == 1 and rows[0]["well_id"] == "XX003"


def test_existence_query(extractor, builder, db):
    q = "Dime si el Pozo CIRA001 tiene cañoneos en el año 2025"
    f = extractor.format_for_query(extractor.extract(q))
    assert "existe" in db.execute(builder.build_query(f))[0]
