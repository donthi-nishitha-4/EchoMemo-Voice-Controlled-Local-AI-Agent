import os
import tempfile
import whisper
from pydub import AudioSegment

os.environ["PATH"] += r";C:\Users\D NISHITHA\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
AudioSegment.converter = r"C:\Users\D NISHITHA\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
AudioSegment.ffmpeg = r"C:\Users\D NISHITHA\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\Users\D NISHITHA\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffprobe.exe"

# Load Whisper model once at module level (no internet needed after first download)
# Options: "tiny", "base", "small", "medium", "large"
# "base" is a good balance of speed and accuracy for most machines
_model = None

def _get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe any audio file (wav, mp3, webm, ogg, m4a) to text.
    Uses OpenAI Whisper running fully locally.
    """
    ext = os.path.splitext(audio_path)[1].lower()

    # Whisper handles wav/mp3/m4a natively
    # For webm/ogg we convert to wav first using pydub
    needs_conversion = ext in {".webm", ".ogg"}

    converted_path = None

    if needs_conversion:
        try:
            sound = AudioSegment.from_file(audio_path)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                sound.export(tmp.name, format="wav")
                converted_path = tmp.name
            path_to_transcribe = converted_path
        except Exception as e:
            return f"Audio conversion error: {str(e)}"
    else:
        path_to_transcribe = audio_path

    try:
        model = _get_model()
        result = model.transcribe(path_to_transcribe)
        text = result["text"].strip()
        if not text:
            text = "Could not understand audio — please speak clearly and try again."
    except Exception as e:
        text = f"Transcription error: {str(e)}"
    finally:
        # Clean up converted temp file if created
        if converted_path and os.path.exists(converted_path):
            try:
                os.remove(converted_path)
            except PermissionError:
                pass  # Windows will clean it up later

    return text
