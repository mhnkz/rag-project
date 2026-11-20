def validate_question(question: str) -> None:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if len(question) > 2000:
        raise ValueError("Question is too long")


def validate_top_k(top_k: int) -> None:
    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
        raise ValueError("top_k must be a positive integer")