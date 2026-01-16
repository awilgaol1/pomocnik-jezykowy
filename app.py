import streamlit as st
from datetime import datetime, timedelta
import io

# --- IMPORTY Z TWOICH MODUŁÓW ---

from utils.audio import generate_audio, speech_to_text
from utils.flashcards import (
    init_db,
    add_flashcard,
    get_flashcards,
    get_flashcards_for_review,
    update_flashcard,
    delete_flashcard,
    add_hard_word,
    get_hard_words,
)
from utils.quiz_q3 import run_quiz_q3
from utils.quiz_c4 import run_quiz_c4
from utils.translator import translate_text
from utils.words import extract_and_normalize
from utils.synonyms import get_synonyms_antonyms

# ---------------------------------------------------------
# KONFIGURACJA APLIKACJI
# ---------------------------------------------------------

st.set_page_config(
    page_title="Language Master — Anna Wilga",
    page_icon="🎧",
    layout="wide"
)

# ---------------------------------------------------------
# INICJALIZACJA BAZY
# ---------------------------------------------------------

init_db()

# ---------------------------------------------------------
# STAN SESJI
# ---------------------------------------------------------

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "default_source_lang" not in st.session_state:
    st.session_state.default_source_lang = "Polski"

if "default_target_lang" not in st.session_state:
    st.session_state.default_target_lang = "Angielski"

if "voice" not in st.session_state:
    st.session_state.voice = "Głos 1 – neutralny"

# ---------------------------------------------------------
# PANEL BOCZNY — USTAWIENIA
# ---------------------------------------------------------

st.sidebar.title("Ustawienia")

st.session_state.api_key = st.sidebar.text_input(
    "Klucz API OpenAI:",
    type="password",
    value=st.session_state.api_key
)

source_lang = st.sidebar.selectbox(
    "Domyślny język źródłowy:",
    ["Polski", "Angielski", "Niemiecki", "Hiszpański", "Włoski", "Francuski"],
    index=0
)
st.session_state.default_source_lang = source_lang

target_lang = st.sidebar.selectbox(
    "Domyślny język docelowy:",
    ["Angielski", "Polski", "Niemiecki", "Hiszpański", "Włoski", "Francuski"],
)
st.session_state.default_target_lang = target_lang

voice_choice = st.sidebar.selectbox(
    "Głos do TTS:",
    ["Głos 1 – neutralny", "Głos 2 – kobiecy", "Głos 3 – męski"],
)
st.session_state.voice = voice_choice

voice_map = {
    "Głos 1 – neutralny": "alloy",
    "Głos 2 – kobiecy": "verse",
    "Głos 3 – męski": "echo"
}

settings = {
    "api_key": st.session_state.api_key,
    "voice": st.session_state.voice,
}

if not st.session_state.api_key:
    st.warning("Wprowadź klucz API w panelu bocznym, aby korzystać z pełnej funkcjonalności.")

# ---------------------------------------------------------
# FUNKCJA SM-2
# ---------------------------------------------------------

def sm2_update(ease_factor, interval, repetitions, quality):
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = int(interval * ease_factor)

        repetitions += 1

    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ease_factor < 1.3:
        ease_factor = 1.3

    next_review = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
    return ease_factor, interval, repetitions, next_review

# ---------------------------------------------------------
# NAGŁÓWEK
# ---------------------------------------------------------

st.title("Language Master — Twoje centrum nauki języków")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "Tłumaczenie + słówka",
    "Fiszki",
    "Quiz Q3",
    "Quiz C4",
    "Nagrywanie + STT",
    "TTS",
    "Synonimy / antonimy",
    "O autorce",
    "Ustawienia"
])

# ---------------------------------------------------------
# TAB 1 — TŁUMACZENIE + WYCIĄGANIE SŁÓWEK (ULEPSZONA WERSJA)
# ---------------------------------------------------------

with tab1:
    st.header("Tłumaczenie tekstu i wyciąganie słówek")

    # --- INICJALIZACJA PAMIĘCI ---
    if "translation" not in st.session_state:
        st.session_state.translation = ""

    if "words" not in st.session_state:
        st.session_state.words = []

    if "words_lang" not in st.session_state:
        st.session_state.words_lang = None

    col1, col2 = st.columns(2)

    # ---------------------------------------------------------
    # LEWA KOLUMNA — wejście
    # ---------------------------------------------------------
    with col1:
        text = st.text_area("Tekst do tłumaczenia:", height=200)

        extract_mode = st.selectbox(
            "Z którego języka wyciągnąć słówka?",
            ["Z tekstu źródłowego", "Z tłumaczenia"]
        )

        src = st.session_state.default_source_lang
        tgt = st.session_state.default_target_lang
        style = "Naturalne"
        formality = "Neutralny"

        if st.button("Przetłumacz i wyciągnij słówka"):
            if not text.strip():
                st.warning("Wpisz tekst.")
            elif not st.session_state.api_key:
                st.error("Brak klucza API.")
            else:
                # ------------------------------
                # TŁUMACZENIE
                # ------------------------------
                with st.spinner("Tłumaczę..."):
                    st.session_state.translation = translate_text(
                        api_key=st.session_state.api_key,
                        text=text,
                        source_lang=src,
                        target_lang=tgt,
                        translation_style=style,
                        formality=formality,
                        force_word=False
                    )

                # ------------------------------
                # WYBÓR ŹRÓDŁA SŁÓWEK
                # ------------------------------
                if extract_mode == "Z tekstu źródłowego":
                    words_text = text
                    st.session_state.words_lang = src
                else:
                    words_text = st.session_state.translation
                    st.session_state.words_lang = tgt

                # ------------------------------
                # WYCIĄGANIE SŁÓWEK
                # ------------------------------
                with st.spinner("Wyciągam słówka..."):
                    try:
                        st.session_state.words = extract_and_normalize(
                            words_text,
                            st.session_state.words_lang
                        )
                    except Exception as e:
                        st.error(f"Błąd ekstrakcji słówek: {e}")
                        st.session_state.words = []

    # ---------------------------------------------------------
    # PRAWA KOLUMNA — wyniki
    # ---------------------------------------------------------
    with col2:
        st.subheader("Tłumaczenie:")
        if st.session_state.translation:
            st.write(st.session_state.translation)
        else:
            st.info("Brak tłumaczenia.")

        st.subheader("Wyciągnięte słówka:")
        if st.session_state.words:

            with st.form("add_words_form"):
                selected_words = st.multiselect(
                    "Wybierz słówka do dodania:",
                    sorted(st.session_state.words)
                )
                submit_words = st.form_submit_button("Dodaj wybrane słówka do fiszek")

            # ---------------------------------------------------------
            # DODAWANIE SŁÓWEK DO FISZEK (POPRAWIONA LOGIKA)
            # ---------------------------------------------------------
            if submit_words and selected_words:
                for w in selected_words:

                    # język słówka (np. angielski)
                    source_lang = st.session_state.words_lang

                    # język użytkownika (np. polski)
                    target_lang = st.session_state.default_source_lang

                    translated = translate_text(
                        api_key=st.session_state.api_key,
                        text=w,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        force_word=True
                    )

                    add_flashcard(w, translated, target_lang)

                st.success(f"Dodano {len(selected_words)} słówek.")

        else:
            st.info("Brak słówek do wyświetlenia.")


# ---------------------------------------------------------
# TAB 2 — FISZKI
# ---------------------------------------------------------

with tab2:
    st.header("Fiszki")

    subtab1, subtab2, subtab3 = st.tabs(["Lista fiszek", "Powtórki SM-2", "Trudne słówka"])

    # ------------------------------
    # LISTA FISZEK
    # ------------------------------
    with subtab1:
        st.subheader("Lista wszystkich fiszek")

        cards = get_flashcards()

        if not cards:
            st.info("Brak fiszek.")
        else:
            for cid, word, translation, lang, level, created in cards:
                col_word, col_trans, col_meta, col_del = st.columns([3, 3, 2, 1])

                with col_word:
                    st.write(f"**{word}**")

                with col_trans:
                    st.write(f"{translation}")

                with col_meta:
                    st.write(f"Język: {lang}")
                    st.write(f"Poziom: {level}")

                with col_del:
                    if st.button("Usuń", key=f"del_{cid}"):
                        delete_flashcard(cid)
                        st.success("Usunięto.")

        # ---------------------------------------------------------
        # EKSPORT DO CSV — minimalny, bez zmian w logice
        # ---------------------------------------------------------
        import pandas as pd

        if cards:
            df = pd.DataFrame(cards, columns=["ID", "Słowo", "Tłumaczenie", "Język", "Poziom", "Data utworzenia"])
            csv_data = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Pobierz fiszki jako CSV",
                data=csv_data,
                file_name="fiszki.csv",
                mime="text/csv"
            )

        st.markdown("---")
        st.subheader("Dodaj fiszkę ręcznie")

        new_word = st.text_input("Słowo:")
        new_translation = st.text_input("Tłumaczenie:")
        new_lang = st.selectbox("Język:", ["Angielski", "Polski", "Niemiecki", "Hiszpański", "Włoski", "Francuski"])

        if st.button("Dodaj fiszkę"):
            if not new_word.strip() or not new_translation.strip():
                st.warning("Uzupełnij pola.")
            else:
                add_flashcard(new_word.strip(), new_translation.strip(), new_lang)
                st.success("Dodano fiszkę.")

    # ------------------------------
    # POWTÓRKI SM-2
    # ------------------------------
    with subtab2:
        st.subheader("Powtórki SM-2")

        review_cards = get_flashcards_for_review()

        if not review_cards:
            st.info("Brak fiszek do powtórki.")
        else:
            cid, word, translation, lang, level, ef, interval, reps, next_review = review_cards[0]

            st.write(f"**{word}**")
            if st.checkbox("Pokaż tłumaczenie"):
                st.write(f"**{translation}**")

            st.write("Jak dobrze pamiętasz?")
            col1, col2, col3, col4, col5 = st.columns(5)
            quality = None

            if col1.button("0", key="q0"):
                quality = 0
            if col2.button("1", key="q1"):
                quality = 1
            if col3.button("3", key="q3"):
                quality = 3
            if col4.button("4", key="q4"):
                quality = 4
            if col5.button("5", key="q5"):
                quality = 5

            if quality is not None:
                new_ef, new_int, new_rep, new_next = sm2_update(ef, interval, reps, quality)
                update_flashcard(cid, new_ef, new_int, new_rep, new_next)
                st.success(f"Następna powtórka: {new_next}")

    # ------------------------------
    # TRUDNE SŁÓWKA
    # ------------------------------
    with subtab3:
        st.subheader("Trudne słówka")

        hard_words = get_hard_words()

        if not hard_words:
            st.info("Brak trudnych słówek.")
        else:
            for word, correct, created in hard_words:
                st.write(f"- {word} → {correct} ({created})")

# ---------------------------------------------------------
# TAB 3 — QUIZ Q3
# ---------------------------------------------------------

with tab3:
    run_quiz_q3(settings)

# ---------------------------------------------------------
# TAB 4 — QUIZ C4
# ---------------------------------------------------------

with tab4:
    run_quiz_c4(settings)

# ---------------------------------------------------------
# ---------------------------------------------------------
# TAB 5 — STT (ULEPSZONA WERSJA Z PAMIĘCIĄ)
# ---------------------------------------------------------

with tab5:
    st.header("Nagrywanie i rozpoznawanie mowy (STT)")

    # Pamięć rozpoznanego tekstu
    if "stt_text" not in st.session_state:
        st.session_state.stt_text = ""

    if not st.session_state.api_key:
        st.error("Brak klucza API.")
    else:
        st.subheader("🎤 Nagrywanie audio")

        # Streamlit Cloud NIE obsługuje st.audio_input, więc sprawdzamy, czy funkcja istnieje
        if hasattr(st, "audio_input"):
            audio_data = st.audio_input("Nagraj swoją wypowiedź:")
        else:
            st.info("Nagrywanie audio nie jest dostępne w Streamlit Cloud.")
            audio_data = None

        # Jeśli nagranie istnieje, pokaż audio player
        if audio_data is not None:
            st.audio(audio_data)

            if st.button("Zamień nagranie na tekst"):
                audio_bytes = audio_data.read()
                text, err = speech_to_text(
                    api_key=st.session_state.api_key,
                    audio_bytes=audio_bytes,
                    language="pl"
                )
                if err:
                    st.error(err)
                else:
                    st.session_state.stt_text = text  # ZAPIS DO PAMIĘCI

    # Wyświetlanie zapamiętanego tekstu
    st.subheader("Rozpoznany tekst:")
    if st.session_state.stt_text:
        st.write(st.session_state.stt_text)
    else:
        st.info("Brak rozpoznanego tekstu.")

    # Przycisk czyszczący
    if st.button("Wyczyść tekst"):
        st.session_state.stt_text = ""

# ---------------------------------------------------------
# TAB 6 — TTS
# ---------------------------------------------------------

with tab6:
    st.header("Generowanie wymowy (TTS)")

    if not st.session_state.api_key:
        st.error("Brak klucza API.")
    else:
        tts_text = st.text_input("Tekst do przeczytania:")
        if st.button("Wygeneruj audio"):
            if not tts_text.strip():
                st.warning("Wpisz tekst.")
            else:
                audio_bytes, err = generate_audio(
                    api_key=st.session_state.api_key,
                    text=tts_text,
                    voice=voice_map[st.session_state.voice]
                )
                if err:
                    st.error(err)
                else:
                    st.success("Audio wygenerowane.")
                    st.audio(audio_bytes, format="audio/mp3")

# ---------------------------------------------------------
# TAB 7 — SYNONIMY
# ---------------------------------------------------------

with tab7:
    st.header("Synonimy i antonimy")

    if not st.session_state.api_key:
        st.error("Brak klucza API.")
    else:
        word = st.text_input("Podaj słowo:")
        lang = st.selectbox("Język:", ["polski", "angielski", "niemiecki", "hiszpański", "włoski", "francuski"])

        if st.button("Pobierz synonimy i antonimy"):
            if not word.strip():
                st.warning("Wpisz słowo.")
            else:
                syn, ant = get_synonyms_antonyms(
                    api_key=st.session_state.api_key,
                    word=word.strip(),
                    language=lang
                )
                st.subheader("Synonimy:")
                st.write(syn if syn else "(brak)")
                st.subheader("Antonimy:")
                st.write(ant if ant else "(brak)")

# ---------------------------------------------------------
# TAB 8 — O AUTORCE
# ---------------------------------------------------------

with tab8:
    st.header("👩‍💻 O autorce — Anna Wilga")

    st.markdown("""
    ### Kim jestem?
    Nazywam się **Anna Wilga** i od lat pasjonuję się nauką języków, technologią oraz tworzeniem narzędzi,
    które realnie pomagają ludziom rozwijać swoje umiejętności.  
    Łączę podejście analityczne z kreatywnością — dlatego powstała ta aplikacja.

    ---

    ### Dlaczego stworzyłam tę aplikację?
    Przez lata korzystałam z wielu narzędzi do nauki języków, ale żadne nie dawało mi pełnej kontroli,
    przejrzystości i możliwości łączenia:
    - tłumaczenia,
    - fiszek,
    - quizów,
    - synonimów,
    - wymowy,
    - nagrywania i analizy mowy.

    Chciałam stworzyć **jedno miejsce**, które:
    - jest intuicyjne,
    - działa szybko,
    - daje użytkownikowi pełną kontrolę,
    - wspiera naukę w sposób naturalny i przyjazny.

    Tak narodził się **Language Master**.

    ---

    ### Kontakt i sugestie
    Jeśli masz pomysł na nową funkcję, chcesz zgłosić błąd lub po prostu podzielić się opinią,
    możesz napisać do mnie:

    📧 **awilga.ol@wp.pl**

    Bardzo doceniam każdy feedback — to dzięki niemu aplikacja może się rozwijać.

    ---

    ### Podziękowania
    Dziękuję wszystkim, którzy testowali pierwsze wersje aplikacji i motywowali mnie do dalszej pracy.
    To dopiero początek — planuję kolejne moduły, ulepszenia i nowe funkcje.

    """)

    st.info("Dziękuję, że korzystasz z Language Master. Życzę Ci pięknej i skutecznej nauki!")

# ---------------------------------------------------------
# TAB 9 — INFORMACJE
# ---------------------------------------------------------

with tab9:
    st.header("Informacje o aplikacji")

    st.write(
        "Aplikacja łączy tłumaczenie, fiszki, quizy, wymowę, "
        "synonimy i antonimy w jednym miejscu."
    )

    st.write("Aktualne ustawienia:")
    st.write(f"- Język źródłowy: {st.session_state.default_source_lang}")
    st.write(f"- Język docelowy: {st.session_state.default_target_lang}")
    st.write(f"- Głos TTS: {st.session_state.voice}")
