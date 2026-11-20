from pathlib import Path
from zipfile import ZipFile

from docx import Document


MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_UNCOMPRESSED_SIZE = 100 * 1024 * 1024


def load_docx(file_path: str) -> str:
    path = Path(file_path)

    if not path.is_file():
        raise ValueError("File does not exist")

    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File is too large")

    if not path.stat().st_size:
        raise ValueError("File is empty")

    try:
        with ZipFile(path) as archive:
            names = archive.namelist()

            if "[Content_Types].xml" not in names:
                raise ValueError("Invalid DOCX file")

            if "word/document.xml" not in names:
                raise ValueError("Invalid DOCX file")

            total_size = sum(
                info.file_size
                for info in archive.infolist()
            )

            if total_size > MAX_UNCOMPRESSED_SIZE:
                raise ValueError("Uncompressed file is too large")

            if archive.testzip() is not None:
                raise ValueError("Corrupted DOCX file")

        document = Document(path)

    except ValueError:
        raise

    except Exception as exc:
        raise ValueError("Invalid DOCX file") from exc

    parts = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            parts.append(text)

    for table in document.tables:
        for row in table.rows:
            cells = [
                cell.text.strip()
                for cell in row.cells
            ]

            parts.append(" | ".join(cells))

    return "\n".join(parts)