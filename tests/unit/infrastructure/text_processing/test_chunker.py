import pytest

from infrastructure.text_processing.chunker import split_text


def test_split_text():
    text = "A" * 2500

    chunks = split_text(
        text,
        chunk_size=1000,
        chunk_overlap=200
    )

    assert len(chunks) == 3
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_empty_text():
    assert split_text("") == []
    assert split_text("   ") == []


def test_small_text():
    text = "Hello RAG"

    chunks = split_text(text)

    assert chunks == [text]


def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        split_text("Hello", chunk_size=0)


def test_invalid_overlap():
    with pytest.raises(ValueError):
        split_text("Hello", chunk_size=100, chunk_overlap=100)


def test_negative_overlap():
    with pytest.raises(ValueError):
        split_text("Hello", chunk_overlap=-1)


def test_non_string_text():
    with pytest.raises(ValueError):
        split_text(None)