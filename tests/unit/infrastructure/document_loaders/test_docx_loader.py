from docx import Document as WordDocument
import pytest

from infrastructure.document_loaders.docx_loader import load_docx


def test_load_docx(tmp_path):
    path = tmp_path / "sample.docx"

    document = WordDocument()
    document.add_paragraph("Hello RAG")
    document.add_paragraph("This is a test document.")

    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Name"
    table.cell(0, 1).text = "Value"

    document.save(path)

    text = load_docx(str(path))

    assert "Hello RAG" in text
    assert "This is a test document." in text
    assert "Name | Value" in text


def test_missing_file(tmp_path):
    path = tmp_path / "missing.docx"

    with pytest.raises(ValueError):
        load_docx(str(path))


def test_invalid_docx(tmp_path):
    path = tmp_path / "invalid.docx"
    path.write_text("This is not a DOCX file")

    with pytest.raises(ValueError):
        load_docx(str(path))


def test_empty_file(tmp_path):
    path = tmp_path / "empty.docx"
    path.touch()

    with pytest.raises(ValueError):
        load_docx(str(path))