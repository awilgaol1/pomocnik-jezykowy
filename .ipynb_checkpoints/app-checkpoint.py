import streamlit as st
import openai
from typing import Optional, Dict
import json

# Konfiguracja strony
st.set_page_config(
    page_title="Pomocnik Językowy",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicjalizacja session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'translation_history' not in st.session_state:
    st.session_state.translation_history = []
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []

# Funkcje pomocnicze
def initialize_openai(api_key: str) -> bool:
    """Inicjalizacja i weryfikacja klucza API OpenAI"""
    try:
        openai.api_key = api_key
        # Test połączenia
        openai.models.list()
        return True
    except Exception as e:
        st.error(f"Błąd weryfikacji klucza API: {str(e)}")
        return False

def detect_language(text: str) -> str:
    """Wykrywa język tekstu używając OpenAI"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem w rozpoznawaniu języków. Odpowiedz TYLKO kodem języka (np. 'en', 'de', 'fr', 'es')."},
                {"role": "user", "content": f"Wykryj język tego tekstu: {text}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        st.error(f"Błąd wykrywania języka: {str(e)}")
        return "unknown"

def translate_text(text: str, source_lang: str, target_lang: str) -> Dict:
    """Tłumaczy tekst z języka źródłowego na docelowy"""
    try:
        language_names = {
            'en': 'angielski', 'de': 'niemiecki', 'fr': 'francuski',
            'es': 'hiszpański', 'it': 'włoski', 'pl': 'polski',
            'ru': 'rosyjski', 'ja': 'japoński', 'zh': 'chiński'
        }
        
        source_name = language_names.get(source_lang, source_lang)
        target_name = language_names.get(target_lang, target_lang)
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Jesteś profesjonalnym tłumaczem. Tłumaczysz z języka {source_name} na {target_name}."},
                {"role": "user", "content": f"Przetłumacz ten tekst:\n\n{text}"}
            ],
            temperature=0.3
        )
        
        translation = response.choices[0].message.content.strip()
        
        return {
            "original": text,
            "translation": translation,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
    except Exception as e:
        st.error(f"Błąd tłumaczenia: {str(e)}")
        return None

# Sidebar - Panel boczny
with st.sidebar:
    st.title("⚙️ Konfiguracja")
    
    # Sekcja API Key
    st.subheader("🔑 Klucz API OpenAI")
    api_key_input = st.text_input(
        "Wprowadź klucz API",
        type="password",
        value=st.session_state.api_key,
        help="Pobierz klucz z https://platform.openai.com/api-keys"
    )
    
    if st.button("Potwierdź klucz"):
        if initialize_openai(api_key_input):
            st.session_state.api_key = api_key_input
            st.success("✅ Klucz API zaakceptowany!")
        else:
            st.error("❌ Nieprawidłowy klucz API")
    
    st.divider()
    
    # Menu nawigacji
    st.subheader("📚 Funkcje")
    page = st.radio(
        "Wybierz funkcję:",
        [
            "🏠 Strona główna",
            "🌐 Tłumaczenie tekstu",
            "🎤 Tłumaczenie z audio",
            "📊 Poziom językowy",
            "📝 Fiszki",
            "🔄 Synonimy i Antonimy",
            "🗣️ Weryfikacja wymowy",
            "✨ Ulepszenie tekstu",
            "📖 Instrukcja",
            "👤 O autorze"
        ],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Status połączenia
    if st.session_state.api_key:
        st.success("🟢 Połączono")
    else:
        st.warning("🔴 Niepołączono")

# Główna zawartość
if not st.session_state.api_key:
    st.title("🌍 Pomocnik Językowy")
    st.warning("⚠️ Wprowadź klucz API OpenAI w panelu bocznym, aby rozpocząć.")
    
    st.markdown("""
    ### Witaj w Pomocniku Językowym! 👋
    
    Ta aplikacja pomoże Ci w nauce języków obcych poprzez:
    - 🌐 Tłumaczenie tekstów i nagrań
    - 📊 Analizę poziomu językowego (A1-C2)
    - 📝 Tworzenie fiszek ze słówek
    - 🗣️ Weryfikację wymowy
    - ✨ Ulepszanie tekstów
    
    **Aby rozpocząć:**
    1. Zarejestruj się na [OpenAI Platform](https://platform.openai.com/)
    2. Wygeneruj klucz API
    3. Wprowadź go w panelu bocznym ⬅️
    """)

elif page == "🏠 Strona główna":
    st.title("🌍 Pomocnik Językowy")
    st.markdown("### Twój osobisty asystent w nauce języków obcych")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**📝 Tłumaczenia**\nAutomatyczne wykrywanie języka i tłumaczenie")
    
    with col2:
        st.info("**📊 Analiza**\nOkreślanie poziomu językowego A1-C2")
    
    with col3:
        st.info("**🎯 Nauka**\nFiszki, wymowa, gramatyka")

elif page == "🌐 Tłumaczenie tekstu":
    st.title("🌐 Tłumaczenie Tekstu")
    
    # Wybór języka docelowego
    target_languages = {
        "Polski": "pl",
        "Angielski": "en",
        "Niemiecki": "de",
        "Francuski": "fr",
        "Hiszpański": "es",
        "Włoski": "it",
        "Rosyjski": "ru"
    }
    
    target_lang_name = st.selectbox(
        "Wybierz język docelowy:",
        list(target_languages.keys())
    )
    target_lang = target_languages[target_lang_name]
    
    # Pole tekstowe
    text_input = st.text_area(
        "Wprowadź tekst do przetłumaczenia:",
        height=200,
        placeholder="Wpisz lub wklej tekst w dowolnym języku..."
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        translate_button = st.button("🔄 Przetłumacz", type="primary")
    
    if translate_button and text_input:
        with st.spinner("Wykrywanie języka i tłumaczenie..."):
            # Wykryj język
            source_lang = detect_language(text_input)
            st.info(f"📍 Wykryty język: **{source_lang.upper()}**")
            
            # Tłumacz
            result = translate_text(text_input, source_lang, target_lang)
            
            if result:
                st.success("✅ Tłumaczenie zakończone!")
                
                # Wyświetl wynik
                st.markdown("### 📄 Wynik tłumaczenia:")
                st.markdown(f"**{result['translation']}**")
                
                # Zapisz w historii
                st.session_state.translation_history.append(result)
                
                # Przyciski akcji
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button("📊 Analizuj poziom", key="analyze_level")
                with col2:
                    st.button("📝 Dodaj do fiszek", key="add_flashcard")
                with col3:
                    st.button("✨ Ulepsz tekst", key="improve_text")

elif page == "🎤 Tłumaczenie z audio":
    st.title("🎤 Tłumaczenie z Nagrania")
    st.info("🚧 Ta funkcja będzie dostępna w Etapie 4")
    st.markdown("""
    **Planowane funkcje:**
    - Nagrywanie audio przez mikrofon
    - Upload plików audio (MP3, WAV)
    - Automatyczne rozpoznawanie mowy
    - Tłumaczenie rozpoznanego tekstu
    """)

elif page == "📊 Poziom językowy":
    st.title("📊 Analiza Poziomu Językowego")
    st.info("🚧 Ta funkcja będzie dostępna w Etapie 2")
    st.markdown("""
    **Planowane funkcje:**
    - Klasyfikacja poziomu A1-C2
    - Analiza użytego słownictwa
    - Wskazówki do poprawy
    - Statystyki zaawansowania
    """)

elif page == "📝 Fiszki":
    st.title("📝 Moje Fiszki")
    st.info("🚧 Ta funkcja będzie dostępna w Etapie 3")
    st.markdown("""
    **Planowane funkcje:**
    - Zapisywanie nieznanych słów
    - System powtórek
    - Kategorie fiszek
    - Eksport/Import
    """)

elif page == "🔄 Synonimy i Antonimy":
    st.title("🔄 Synonimy i Antonimy")
    st.info("🚧 Ta funkcja będzie dostępna w Etapie 3")

elif page == "🗣️ Weryfikacja wymowy":
    st.title("🗣️ Weryfikacja Wymowy")
    st.info("🚧 Ta funkcja będzie dostępna w Etapie 4")

elif page == "✨ Ulepszenie tekstu":
    st.title("✨ Ulepszenie Tekstu AI")
    st.info("🚧 Ta funkcja będzie dostępna w Etapie 5")

elif page == "📖 Instrukcja":
    st.title("📖 Instrukcja Użytkownika")
    
    st.markdown("""
    ## Jak korzystać z Pomocnika Językowego?
    
    ### 1️⃣ Konfiguracja
    - Wprowadź klucz API OpenAI w panelu bocznym
    - Wybierz funkcję z menu
    
    ### 2️⃣ Tłumaczenie tekstu
    - Wklej lub wpisz tekst
    - Wybierz język docelowy
    - Kliknij "Przetłumacz"
    
    ### 3️⃣ Analiza i nauka
    - Sprawdź poziom językowy tekstu
    - Dodaj nieznane słowa do fiszek
    - Ćwicz wymowę
    
    ### 4️⃣ Tryb prywatny
    - Wszystkie dane są lokalne
    - Nic nie jest udostępniane innym użytkownikom
    
    ### 🆘 Pomoc
    Jeśli masz pytania, skontaktuj się z autorem.
    """)

elif page == "👤 O autorze":
    st.title("👤 O Autorze")
    
    st.markdown("""
    ## Pomocnik Językowy
    
    **Wersja:** 1.0.0 (Etap 1)  
    **Data wydania:** Styczeń 2026
    
    ### 📧 Kontakt
    - **Email:** kontakt@pomocnikjezykowy.pl
    - **GitHub:** github.com/pomocnikjezykowy
    
    ### 🛠️ Technologie
    - Python 3.11+
    - Streamlit
    - OpenAI GPT-4
    - Whisper API (audio)
    
    ### 📜 Licencja
    MIT License - Wolne oprogramowanie
    
    ### 🙏 Podziękowania
    Dziękuję za korzystanie z aplikacji!
    """)

# Footer
st.divider()
st.caption("Pomocnik Językowy v1.0 | Powered by OpenAI | Made with ❤️ by [Anna Wilga]")