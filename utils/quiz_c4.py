import streamlit as st
import random
from utils.flashcards import get_flashcards
from utils.audio import generate_audio


def run_quiz_c4(settings):
    st.header("🔊 Wymowa (C4) — zgadnij słowo po wymowie")

    cards = get_flashcards()

    if not cards:
        st.info("Brak fiszek do quizu wymowy.")
        return

    # Inicjalizacja stanu quizu
    if "quiz_c4" not in st.session_state:
        st.session_state.quiz_c4 = {
            "current_word": None,
            "options": [],
            "correct": None,
            "score": 0,
            "total": 0
        }

    quiz = st.session_state.quiz_c4

    # Jeśli nie ma aktywnego pytania — generujemy nowe
    if quiz["current_word"] is None:
        card = random.choice(cards)
        cid, word, translation, lang, level, created = card[:6]

        # Losowanie błędnych opcji
        wrong = [c[1] for c in cards if c[1] != word]
        wrong = random.sample(wrong, min(3, len(wrong)))

        options = wrong + [word]
        random.shuffle(options)

        quiz["current_word"] = word
        quiz["options"] = options
        quiz["correct"] = word

    # Odtwarzanie audio
    st.subheader("🔉 Odsłuchaj słowo:")

    voice_map = {
        "Głos 1 – neutralny": "alloy",
        "Głos 2 – kobiecy": "verse",
        "Głos 3 – męski": "echo"
    }

    audio_bytes, error = generate_audio(
        api_key=settings["api_key"],
        text=quiz["current_word"],
        voice=voice_map[settings["voice"]]
    )

    if error:
        st.error(error)
    else:
        st.audio(audio_bytes, format="audio/mp3")

    # Opcje odpowiedzi
    selected = st.radio("Co to za słowo?", quiz["options"], key=f"c4_{quiz['total']}")

    if st.button("Zatwierdź odpowiedź", key="c4_submit"):
        quiz["total"] += 1

        if selected == quiz["correct"]:
            quiz["score"] += 1
            st.success("Poprawnie! 🎉")
        else:
            st.error(f"Niepoprawnie. Poprawna odpowiedź to: **{quiz['correct']}**.")

        # Reset pytania
        quiz["current_word"] = None
        st.rerun()

    # Statystyki
    if quiz["total"] > 0:
        st.write("---")
        st.subheader("📊 Statystyki")
        st.write(f"Poprawne odpowiedzi: **{quiz['score']}**")
        st.write(f"Łącznie pytań: **{quiz['total']}**")
        percent = int((quiz["score"] / quiz["total"]) * 100)
        st.write(f"Skuteczność: **{percent}%**")

    # Reset quizu
    if st.button("🔁 Zacznij od nowa"):
        st.session_state.quiz_c4 = {
            "current_word": None,
            "options": [],
            "correct": None,
            "score": 0,
            "total": 0
        }
        st.rerun()
