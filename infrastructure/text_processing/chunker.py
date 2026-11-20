from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[str]:
    if not isinstance(text, str):
        raise ValueError("Text must be a string")

    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    return splitter.split_text(text)