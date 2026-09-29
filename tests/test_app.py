import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(__import__("pathlib").Path(__file__).parent.parent / "app.py")


def test_app_answers_question():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    at.chat_input[0].set_value("Al pozo XX001 cuantos cañoneos ha tenido en el año 2020").run()
    assert not at.exception
    assert "XX001" in at.chat_message[-1].markdown[0].value


def test_app_asks_for_clarification():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.chat_input[0].set_value("¿El pozo XX005 tuvo alguna intervención en 2021?").run()
    assert "¿A qué tipo de intervención" in at.chat_message[-1].markdown[0].value
