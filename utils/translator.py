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

    # --- TŁUMACZENIE JEDNEGO SŁOWA ---
    if force_word:
        prompt = (
            f"Przetłumacz dokładnie jedno słowo: '{text}'.\n"
            f"Tłumacz z {source_lang} na {target_lang}.\n"
            f"Zawsze podaj tłumaczenie — nawet jeśli słowo wygląda podobnie.\n"
            f"Nie zwracaj słowa wejściowego. Nie podawaj wyjaśnień.\n"
            f"Zwróć tylko jedno słowo w języku docelowym."
        )

    # --- TŁUMACZENIE ZDANIA / TEKSTU ---
    else:
        prompt = (
            f"Przetłumacz tekst z {source_lang} na {target_lang}.\n"
            f"Styl: {translation_style}. Formalność: {formality}.\n"
            f"Tekst: {text}\n"
            f"Zwróć tylko tłumaczenie, bez komentarzy ani wyjaśnień."
        )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )

        result = response.choices[0].message.content.strip()

        # --- WYMUSZENIE: jeśli model zwróci to samo słowo ---
        if force_word and result.lower() == text.lower():
            prompt_retry = (
                f"Popraw tłumaczenie słowa '{text}' z {source_lang} na {target_lang}.\n"
                f"Nie powtarzaj słowa wejściowego. Podaj jedno słowo w języku docelowym."
            )

            retry = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt_retry}],
                temperature=0.0,
                max_tokens=20
            )

            return retry.choices[0].message.content.strip()

        return result

    except Exception as e:
        return f"[Błąd tłumaczenia: {e}]"
