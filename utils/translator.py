from openai import OpenAI

def translate_text(
    api_key,
    text,
    source_lang,
    target_lang,
    translation_style="Naturalne",
    formality="Neutralny",
    model="gpt-4o-mini",
    temperature=0.2,
    max_tokens=200,
    force_word=False
):
    client = OpenAI(api_key=api_key)

    if force_word:
        prompt = (
            f"Przetłumacz TYLKO to jedno słowo: '{text}'. "
            f"Nie zmieniaj formy, nie poprawiaj, nie zgaduj. "
            f"Podaj najprostsze możliwe tłumaczenie z {source_lang} na {target_lang}."
        )
    else:
        prompt = (
            f"Przetłumacz tekst z {source_lang} na {target_lang}. "
            f"Styl: {translation_style}. Formalność: {formality}. "
            f"Tekst: {text}"
        )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[Błąd tłumaczenia: {e}]"
