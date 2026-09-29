import pytest

from mini_attention import EntityExtractor, QueryBuilder, WellDatabase


@pytest.fixture(scope="session")
def db(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "wells.db"
    return WellDatabase(db_path=str(path), seed=42)


@pytest.fixture
def extractor():
    return EntityExtractor()


@pytest.fixture
def builder():
    return QueryBuilder(db_type="sqlite")
