import io
from openai import OpenAI

def generate_audio(api_key, text, voice="alloy"):
    """
    Generuje audio MP3 z tekstu.
    voice: alloy / verse / echo
    """
    try:
        client = OpenAI(api_key=api_key)

        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text
        )

        audio_bytes = response.read()
        return audio_bytes, None

    except Exception as e:
        return None, f"Błąd generowania audio: {e}"


def speech_to_text(api_key, audio_bytes, language="pl"):
    """
    Zamienia nagranie głosu na tekst.
    language: pl / en / de / it / es
    """
    try:
        client = OpenAI(api_key=api_key)

        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "input_audio.wav"

        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file,
            language=language
        )

        return transcript.text, None

    except Exception as e:
        return None, f"Błąd rozpoznawania mowy: {e}"
