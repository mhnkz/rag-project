import pytest

from domain.rag.validators import validate_question, validate_top_k


def test_valid_question():
    validate_question("What is RAG?")


def test_empty_question():
    with pytest.raises(ValueError):
        validate_question("")


def test_whitespace_question():
    with pytest.raises(ValueError):
        validate_question("   ")


def test_long_question():
    with pytest.raises(ValueError):
        validate_question("a" * 2001)


def test_valid_top_k():
    validate_top_k(5)


@pytest.mark.parametrize("value", [0, -1, True, 1.5, "5", None])
def test_invalid_top_k(value):
    with pytest.raises(ValueError):
        validate_top_k(value)