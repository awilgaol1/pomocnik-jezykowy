import re

def extract_and_normalize(text: str):
    """
    Wyciąga słowa z tekstu i normalizuje je do małych liter.
    Obsługuje języki europejskie (litery A–Z + akcenty).
    """
    if not text:
        return []

    # Wyciąganie słów (litery + akcenty)
    words = re.findall(r"[A-Za-zÀ-ž]+", text)

    # Normalizacja do małych liter
    normalized = [w.lower() for w in words]

    # Usunięcie duplikatów przy zachowaniu kolejności
    seen = set()
    unique_words = []
    for w in normalized:
        if w not in seen:
            seen.add(w)
            unique_words.append(w)

    return unique_words
