import spacy
import re

# Modele spaCy
MODELS = {
    "Polski": "pl_core_news_sm",
    "Angielski": "en_core_web_sm"
}

loaded_models = {}

def get_model(lang):
    """Ładuje model spaCy tylko raz."""
    if lang not in loaded_models:
        model_name = MODELS.get(lang)
        if model_name:
            loaded_models[lang] = spacy.load(model_name)
        else:
            raise ValueError(f"Brak modelu spaCy dla języka: {lang}")
    return loaded_models[lang]


def extract_words(text: str):
    """
    Wyciąga słowa z tekstu:
    - NIE niszczy skrótów typu API, AI, GPT
    - NIE zmienia liter wewnątrz słów
    - usuwa interpunkcję, ale zachowuje cyfry i wielkie litery
    """
    # Zamieniamy tylko znaki interpunkcyjne na spacje
    text = re.sub(r"[^\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]", " ", text)

    # Rozbijamy na słowa
    words = text.split()

    # Usuwamy duplikaty, ale NIE usuwamy krótkich słów
    return list(set(words))


def lemmatize_words(words, lang):
    """
    Lematizacja:
    - zachowuje słowa techniczne (API, AI, GPT)
    - zwraca pełne formy podstawowe, nie okaleczone rdzenie
    """
    nlp = get_model(lang)

    lemmas = []
    for w in words:

        # Słowa techniczne zostawiamy bez zmian
        if w.isupper() and len(w) <= 6:
            lemmas.append(w)
            continue

        doc = nlp(w)
        lemma = doc[0].lemma_

        # Naprawa okaleczonych rdzeni typu "stabl" → "stable"
        if len(lemma) <= 4 and w.lower().startswith(lemma):
            lemmas.append(w.lower())
        else:
            lemmas.append(lemma)

    return list(set(lemmas))

def extract_and_normalize(text: str, lang: str):
    """
    Główna funkcja:
    1. wyciąga słowa
    2. normalizuje je
    3. zwraca listę unikalnych słówek
    """
    words = extract_words(text)
    lemmas = lemmatize_words(words, lang)
    return lemmas
