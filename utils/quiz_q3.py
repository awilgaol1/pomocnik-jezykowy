import streamlit as st
import random
from utils.flashcards import get_flashcards


def run_quiz_q3(settings):
    st.header("🧪 Quiz Q3 — Test wielokrotnego wyboru")

    cards = get_flashcards()

    if not cards:
        st.info("Brak fiszek do quizu.")
        return

    # Suwak liczby pytań
    num_questions = st.slider("Liczba pytań w quizie:", 5, 30, 10)

    # Inicjalizacja stanu
    if "quiz_q3" not in st.session_state:
        st.session_state.quiz_q3 = {
            "questions": [],
            "current": 0,
            "score": 0,
            "mistakes": []
        }

    # Reset quizu przy zmianie liczby pytań
    if "last_num_questions" not in st.session_state:
        st.session_state.last_num_questions = num_questions

    if st.session_state.last_num_questions != num_questions:
        st.session_state.quiz_q3 = {
            "questions": [],
            "current": 0,
            "score": 0,
            "mistakes": []
        }
        st.session_state.last_num_questions = num_questions

    quiz = st.session_state.quiz_q3

    # Generowanie pytań
    if not quiz["questions"]:
        all_cards = cards.copy()
        random.shuffle(all_cards)
        selected = all_cards[:num_questions]

        questions = []
        for card in selected:
            cid, word, translation, lang, level, created = card[:6]

            wrong = [c[2] for c in cards if c[0] != cid]
            wrong = random.sample(wrong, min(3, len(wrong)))

            options = wrong + [translation]
            random.shuffle(options)

            questions.append({
                "word": word,
                "correct": translation,
                "options": options
            })

        quiz["questions"] = questions

    # Jeśli quiz trwa
    if quiz["current"] < len(quiz["questions"]):
        q = quiz["questions"][quiz["current"]]

        st.subheader(f"Pytanie {quiz['current'] + 1} / {len(quiz['questions'])}")
        st.progress((quiz["current"] + 1) / len(quiz["questions"]))

        st.write(f"Co oznacza słowo: **{q['word']}**?")

        selected = st.radio("Wybierz odpowiedź:", q["options"], key=f"q3_{quiz['current']}")

        if st.button("Zatwierdź odpowiedź"):
            if selected == q["correct"]:
                quiz["score"] += 1
            else:
                quiz["mistakes"].append((q["word"], q["correct"]))

            quiz["current"] += 1
            st.rerun()

    # KONIEC QUIZU
    else:
        st.success("🎉 Quiz zakończony!")

        total = len(quiz["questions"])
        score = quiz["score"]
        percent = int((score / total) * 100)

        st.subheader(f"Wynik końcowy: **{score}/{total} ({percent}%)**")

        # Pochwały zależne od wyniku
        if percent >= 90:
            st.info("🔥 Rewelacja! Twoja znajomość słówek robi wrażenie.")
        elif percent >= 70:
            st.info("💪 Świetnie Ci idzie! Jeszcze trochę i będzie perfekcyjnie.")
        elif percent >= 50:
            st.info("👍 Dobra robota! Fundamenty są, teraz je tylko wzmocnić.")
        else:
            st.info("🌱 Każdy mistrz zaczynał od podstaw. Dasz radę!")

        # Błędy
        if quiz["mistakes"]:
            st.subheader("❌ Twoje błędy:")
            for w, correct in quiz["mistakes"]:
                st.write(f"- **{w}** → poprawnie: **{correct}**")

        # ⭐ TRUDNE SŁÓWKA — zapis z błędów
        # lista krotek: (słowo, poprawne tłumaczenie)
        st.session_state.hard_words = quiz["mistakes"][:]

        st.subheader("⭐ Rekomendacje:")
        st.write("- przejrzyj błędne słówka w fiszkach")
        st.write("- zrób quiz ponownie za kilka godzin")
        st.write("- powtórz słówka w trybie SM‑2")

        if st.button("🔁 Zrób quiz ponownie"):
            st.session_state.quiz_q3 = {
                "questions": [],
                "current": 0,
                "score": 0,
                "mistakes": []
            }
            st.rerun()
