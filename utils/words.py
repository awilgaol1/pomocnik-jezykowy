import spacy
import re

MODELS = {
    "Polski": "pl_core_news_sm",
    "Angielski": "en_core_web_sm"
}

loaded_models = {}

def get_model(lang):
    if lang not in loaded_models:
        model_name = MODELS.get(lang)
        if not model_name:
            raise ValueError(f"Brak modelu spaCy dla języka: {lang}")

        try:
            loaded_models[lang] = spacy.load(model_name)
        except OSError:
            raise RuntimeError(
                f"Model spaCy '{model_name}' nie jest zainstalowany. "
                f"Zainstaluj go poleceniem: python -m spacy download {model_name}"
            )

    return loaded_models[lang]


def extract_words(text: str):
    text = re.sub(r"[^\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]", " ", text)
    words = text.split()
    return list(set(words))


def lemmatize_words(words, lang):
    nlp = get_model(lang)
    lemmas = []

    for w in words:
        if re.fullmatch(r"[A-Z0-9\-]{2,10}", w):
            lemmas.append(w)
            continue

        doc = nlp(w)
        lemma = doc[0].lemma_

        if len(lemma) <= 4 and w.lower().startswith(lemma):
            lemmas.append(w.lower())
        else:
            lemmas.append(lemma)

    return list(set(lemmas))


def extract_and_normalize(text: str, lang: str):
    words = extract_words(text)
    lemmas = lemmatize_words(words, lang)
    return lemmas
