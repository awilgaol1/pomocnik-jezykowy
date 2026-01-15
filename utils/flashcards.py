import sqlite3
from datetime import datetime

DB_PATH = "flashcards.db"


# ---------------------------------------------------------
# INICJALIZACJA BAZY
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Tabela fiszek
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            translation TEXT NOT NULL,
            language TEXT NOT NULL,
            level INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            interval INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            next_review TEXT,
            created TEXT
        )
    """)

    # NOWA tabela trudnych słówek
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hard_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            correct_translation TEXT NOT NULL,
            created TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# FISZKI — DODAWANIE
# ---------------------------------------------------------
def add_flashcard(word, translation, language):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO flashcards (word, translation, language, created)
        VALUES (?, ?, ?, ?)
    """, (word, translation, language, created))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# FISZKI — POBIERANIE WSZYSTKICH
# ---------------------------------------------------------
def get_flashcards():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, word, translation, language, level, created
        FROM flashcards
        ORDER BY created DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------
# FISZKI — DO POWTÓREK SM-2
# ---------------------------------------------------------
def get_flashcards_for_review():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        SELECT id, word, translation, language, level,
               ease_factor, interval, repetitions, next_review
        FROM flashcards
        WHERE next_review IS NULL OR next_review <= ?
        ORDER BY next_review ASC
    """, (today,))

    rows = cur.fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------
# FISZKI — AKTUALIZACJA SM-2
# ---------------------------------------------------------
def update_flashcard(cid, ease_factor, interval, repetitions, next_review):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE flashcards
        SET ease_factor = ?, interval = ?, repetitions = ?, next_review = ?
        WHERE id = ?
    """, (ease_factor, interval, repetitions, next_review, cid))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# FISZKI — USUWANIE
# ---------------------------------------------------------
def delete_flashcard(cid):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM flashcards WHERE id = ?", (cid,))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# TRUDNE SŁÓWKA — DODAWANIE
# ---------------------------------------------------------
def add_hard_word(word, correct_translation):
    """Dodaje trudne słowo do tabeli hard_words, jeśli jeszcze go tam nie ma."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # sprawdzamy, czy już istnieje
    cur.execute("""
        SELECT COUNT(*) FROM hard_words
        WHERE word = ? AND correct_translation = ?
    """, (word, correct_translation))

    exists = cur.fetchone()[0]

    if not exists:
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO hard_words (word, correct_translation, created)
            VALUES (?, ?, ?)
        """, (word, correct_translation, created))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# TRUDNE SŁÓWKA — POBIERANIE
# ---------------------------------------------------------
def get_hard_words():
    """Zwraca listę trudnych słówek z bazy."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT word, correct_translation, created
        FROM hard_words
        ORDER BY created DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows
