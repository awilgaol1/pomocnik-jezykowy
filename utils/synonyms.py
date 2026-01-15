from openai import OpenAI
import re

def get_synonyms_antonyms(api_key, word, language):
    client = OpenAI(api_key=api_key)

    prompt = f"""
Podaj kilka synonimów i antonimów dla słowa: "{word}".
Odpowiadaj w języku: {language}.
Użyj wyraźnych nagłówków:

Synonimy:
...
Antonimy:
...
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.2
        )

        text = response.choices[0].message.content.strip()

        # Normalizacja nagłówków
        normalized = text
        normalized = re.sub(r"Synonyms?:", "Synonimy:", normalized, flags=re.I)
        normalized = re.sub(r"Antonyms?:", "Antonimy:", normalized, flags=re.I)

        syn = ""
        ant = ""

        if "Synonimy:" in normalized:
            syn = normalized.split("Synonimy:")[1].split("Antonimy:")[0].strip()

        if "Antonimy:" in normalized:
            ant = normalized.split("Antonimy:")[1].strip()

        # Jeśli nadal nic nie ma — zwróć cały tekst jako synonimy
        if not syn and not ant:
            syn = text

        return syn, ant

    except Exception as e:
        return f"Błąd: {e}", ""
