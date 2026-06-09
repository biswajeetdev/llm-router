COMPLEX_KEYWORDS = {
    "analyze", "compare", "contrast", "evaluate", "critique",
    "architect", "design", "implement", "debug", "refactor",
    "optimize", "review", "explain in detail", "step by step",
    "comprehensively", "thoroughly", "write a", "create a",
    "build a", "develop", "generate code", "write code",
}

SIMPLE_KEYWORDS = {
    "summarize", "extract", "translate", "format", "convert",
    "list", "define", "what is", "who is", "when did",
    "spell check", "fix grammar", "paraphrase", "shorten",
    "yes or no", "true or false",
}


def count_tokens(text: str) -> int:
    # rough estimate: 1 token ≈ 4 chars
    return len(text) // 4


def classify(prompt: str) -> str:
    """Classify prompt complexity as 'simple', 'medium', or 'complex'."""
    tokens = count_tokens(prompt)
    text_lower = prompt.lower()

    if tokens > 1500:
        return "complex"
    elif tokens < 100:
        base = "simple"
    elif tokens < 500:
        base = "medium"
    else:
        base = "complex"

    complex_hits = sum(1 for k in COMPLEX_KEYWORDS if k in text_lower)
    simple_hits = sum(1 for k in SIMPLE_KEYWORDS if k in text_lower)

    if complex_hits >= 2:
        return "complex"
    if complex_hits == 1 and base == "simple":
        return "medium"
    if simple_hits >= 2 and base == "medium":
        return "simple"
    if simple_hits >= 1 and base == "complex" and tokens < 800:
        return "medium"

    return base
