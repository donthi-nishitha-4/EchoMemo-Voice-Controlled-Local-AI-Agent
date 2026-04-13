import streamlit as st
import tempfile
import os

from models.stt import transcribe_audio
from llm.intent_classifier import classify_intent
from tools.file_tools import create_file_from_text
from tools.code_tools import generate_code_file
from tools.text_tools import summarize_text


try:
    from streamlit_mic_recorder import mic_recorder
    MIC_AVAILABLE = True
except Exception:
    MIC_AVAILABLE = False

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="🎶EchoMemo", layout="wide")
st.title("🔊EchoMemo: Voice Controlled Local AI Agent🎵")
st.caption("Speak or upload audio → Transcribed → Intent detected → Action executed locally")

# ── Input section ──────────────────────────────────────────────────────────────
st.subheader("1️⃣  Provide Audio Input")
col1, col2 = st.columns(2)

audio_bytes: bytes | None = None
audio_source: str = ""          # track where audio came from for suffix detection

with col1:
    st.markdown("#### 🎤 Record from Microphone")
    if MIC_AVAILABLE:
        mic_audio = mic_recorder(
            start_prompt="▶ Start Recording",
            stop_prompt="⏹ Stop Recording",
            key="mic"
        )
        if mic_audio and mic_audio.get("bytes"):
            audio_bytes = mic_audio["bytes"]
            audio_source = "mic"
            st.success("Microphone audio captured ✅")
            st.audio(audio_bytes, format="audio/webm")
    else:
        st.info(
            "Microphone not available.\n\n"
            "Install with: `pip install streamlit-mic-recorder`"
        )

with col2:
    st.markdown("#### 📂 Upload Audio File")
    uploaded_audio = st.file_uploader(
        "Supports WAV, MP3, M4A, OGG, WEBM",
        type=["wav", "mp3", "m4a", "ogg", "webm"]
    )
    if uploaded_audio is not None:
        audio_bytes = uploaded_audio.read()
        audio_source = "upload"
        # Capture the actual extension from the uploaded filename
        upload_ext = os.path.splitext(uploaded_audio.name)[1].lower() or ".wav"
        st.success(f"Audio uploaded: `{uploaded_audio.name}` ✅")
        st.audio(audio_bytes, format=f"audio/{upload_ext.lstrip('.')}")

# ── Pipeline ───────────────────────────────────────────────────────────────────
if audio_bytes:
    # Determine correct suffix for the temp file
    if audio_source == "mic":
        file_suffix = ".webm"          # streamlit-mic-recorder always outputs webm
    elif audio_source == "upload":
        file_suffix = upload_ext       # use the real extension so pydub handles it right
    else:
        file_suffix = ".wav"

    # Write bytes to a named temp file (don't delete immediately — we read it next)
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp:
        tmp.write(audio_bytes)
        temp_audio_path = tmp.name

    try:
        # ── Step 1: Speech-to-Text ─────────────────────────────────────────────
        st.divider()
        st.subheader("2️⃣  Transcription")
        with st.spinner("Transcribing audio with Whisper…"):
            transcription = transcribe_audio(temp_audio_path)
        st.success(transcription)

        # ── Step 2: Intent Classification ──────────────────────────────────────
        st.subheader("3️⃣  Detected Intent")
        with st.spinner("Classifying intent with LLM…"):
            intent = classify_intent(transcription)

        intent_labels = {
            "create_file":    "📄 Create File",
            "write_code":     "💻 Write Code",
            "summarize_text": "📋 Summarize Text",
            "general_chat":   "💬 General Chat",
        }
        st.info(f"**{intent_labels.get(intent, intent)}** (`{intent}`)")

        # ── Step 3: Tool Execution ─────────────────────────────────────────────
        st.subheader("4️⃣  Action & Result")

        if intent == "create_file":
            with st.spinner("Creating file…"):
                result = create_file_from_text(transcription)
            st.success(result)

        elif intent == "write_code":
            with st.spinner("Generating code with LLM…"):
                path, code = generate_code_file("generated_code.py", transcription)
            st.success(f"Code saved to `{path}`")
            st.code(code, language="python")

        elif intent == "summarize_text":
            with st.spinner("Summarizing with LLM…"):
                result = summarize_text(transcription)
            st.markdown(result)

        else:
            # General chat — pass through to LLM directly
            import ollama
            with st.spinner("Thinking…"):
                try:
                    response = ollama.chat(
                        model="llama3",
                        messages=[{"role": "user", "content": transcription}]
                    )
                    result = response["message"]["content"]
                except Exception as e:
                    result = f"LLM error: {str(e)}"
            st.markdown(result)

    finally:
        # Windows fix: close any handles before deleting
        try:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
        except PermissionError:
            pass  # Windows will clean it up when the process ends

else:
    st.info("⏺️ Record from your microphone or upload an audio file to begin.")
