import re

def clean_text(text: str) -> str:
    # Replaces spaces and tabs with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Replaces multiple new lines with a single one
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Removes awkward line breaks
    # text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    return text.strip()