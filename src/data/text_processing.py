import re

def tokenize(text: str) -> list[str]:
    # Mkae the whole text lower case
    text = text.lower()

    # Removes punctuation and special characters
    text = re.sub(r"[^a-z0-9\s']", " " , text)

    # Removes Multiple whitespace into one whitespace
    text = re.sub(r"\s+" , " " , text).strip()

    # Return a list of tokens
    return text.split()

