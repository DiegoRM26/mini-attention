from mini_attention import WellDatabase


def test_database_has_sample_data(db):
    assert db.total_records() > 50
    assert "XX001" in db.list_wells()


def test_seed_is_deterministic(tmp_path):
    a = WellDatabase(db_path=str(tmp_path / "a.db"), seed=42)
    b = WellDatabase(db_path=str(tmp_path / "b.db"), seed=42)
    assert a.get_well_summary("XX001") == b.get_well_summary("XX001")


def test_well_summary_is_sorted_and_scoped(db):
    rows = db.get_well_summary("XX001")
    assert rows and all(r["event_type"] for r in rows)
