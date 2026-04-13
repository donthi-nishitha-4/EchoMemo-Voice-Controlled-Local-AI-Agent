# 🔊 EchoMemo: Voice-Controlled Local AI Agent🎵

A fully local voice agent that accepts audio input (microphone or file upload), transcribes it using Whisper, classifies the intent using LLaMA 3 (via Ollama), executes the appropriate tool, and displays the full pipeline in a Streamlit UI — all running on your local machine with no cloud API keys required.

## 🎬 Demo Video


## 📝 Technical Article



## 🏗️ Architecture

```
Audio Input (mic / file upload)
        │
        ▼
  Speech-to-Text          ← OpenAI Whisper "base" model (fully local)
  [models/stt.py]
        │
        ▼
  Intent Classifier       ← LLaMA 3 via Ollama (fully local)
  [llm/intent_classifier.py]
        │
        ├── create_file    → tools/file_tools.py   → output/
        ├── write_code     → tools/code_tools.py   → output/
        ├── summarize_text → tools/text_tools.py
        └── general_chat  → direct Ollama LLaMA 3 chat
        │
        ▼
  Streamlit UI            ← displays transcription, intent, action, result
  [app.py]
```

### Component Breakdown

| Component | File | Technology |
|-----------|------|------------|
| UI | `app.py` | Streamlit + streamlit-mic-recorder |
| Speech-to-Text | `models/stt.py` | OpenAI Whisper (`base` model, local) |
| Intent Classification | `llm/intent_classifier.py` | LLaMA 3 via Ollama |
| File Creation | `tools/file_tools.py` | Python stdlib |
| Code Generation | `tools/code_tools.py` | LLaMA 3 via Ollama |
| Text Summarization | `tools/text_tools.py` | LLaMA 3 via Ollama |


## ⚙️ Setup Instructions

### 1. System Prerequisites

#### Install ffmpeg
ffmpeg is required by pydub for audio format conversion.

**Windows (recommended):**
```
winget install ffmpeg
```
After installing, run `where ffmpeg` in CMD to get the exact path — you will need it in Step 4.

**macOS:**
```
brew install ffmpeg
```

**Ubuntu / Debian:**
```
sudo apt install ffmpeg
```

#### Install Ollama + LLaMA 3
Download Ollama from https://ollama.com and then run:
```
ollama pull llama3
```



### 2. Clone the Repository
Download or clone this repo to your local machine.



### 3. Create a Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
```


### 4. Windows ffmpeg Path Fix
Because winget installs ffmpeg in a long path, you need to set it explicitly in `models/stt.py`.

Run `where ffmpeg` in CMD and copy the output path. Then open `models/stt.py` and update these lines at the top with your actual path:

```python
os.environ["PATH"] += r";C:\YOUR\FFMPEG\PATH\bin"
AudioSegment.converter = r"C:\YOUR\FFMPEG\PATH\bin\ffmpeg.exe"
AudioSegment.ffmpeg    = r"C:\YOUR\FFMPEG\PATH\bin\ffmpeg.exe"
AudioSegment.ffprobe   = r"C:\YOUR\FFMPEG\PATH\bin\ffprobe.exe"
```

> macOS/Linux users can skip this step — ffmpeg will be found automatically.



### 5. Install Python Dependencies
```bash
pip install -r requirements.txt
```

> **Note:** On first run, Whisper will automatically download the `base` model (~145 MB). This only happens once.


### 6. Run the App
```bash
python -m streamlit run app.py
```

The app will open at `http://localhost:8501`


## 🎯 Supported Intents

| Intent | Example voice commands | Action |
|--------|----------------------|--------|
| `create_file` | "Create a file called notes", "Make a new file named todo" | Creates a `.txt` file in `output/` |
| `write_code` | "Write a Python function for retry logic", "Create a script that sorts a list" | Generates Python code and saves to `output/` |
| `summarize_text` | "Summarize this: ...", "Give me a brief summary of..." | Returns a 5-point bullet summary |
| `general_chat` | "What is machine learning?", "Tell me a joke" | LLM responds conversationally |

> ⚠️ To ensure safety, all file and code creation is strictly sandboxed to the `output/` directory.


## 🎤 Input Methods

- **Microphone** — click "Start Recording", speak your command, click "Stop Recording"
- **File Upload** — supports `.wav`, `.mp3`, `.m4a`, `.ogg`, `.webm`


## 🔧 Hardware Notes & Workarounds

### Speech-to-Text: Whisper (local)
Uses `openai-whisper` with the `base` model (~145 MB), running fully locally on CPU. No API key needed.

**If your machine is too slow**, use a smaller model by changing this line in `models/stt.py`:
```python
_model = whisper.load_model("tiny")   # fastest, least accurate
_model = whisper.load_model("small")  # good middle ground
```

### LLM: LLaMA 3 via Ollama (local)
The `llama3` 8B model requires ~6 GB RAM. If your machine struggles, use a lighter model:
```bash
ollama pull llama3.2:1b
```
Then change `model="llama3"` to `model="llama3.2:1b"` across all tool files.


## 📁 Project Structure

```
voice-agent/
├── app.py                       # Streamlit UI + pipeline orchestration
├── requirements.txt
├── README.md
├── .gitignore
├── output/                      # All generated files land here (sandboxed)
│   └── .gitkeep
├── models/
│   ├── __init__.py
│   └── stt.py                   # Whisper speech-to-text
├── llm/
│   ├── __init__.py
│   └── intent_classifier.py     # LLaMA 3 intent classification
└── tools/
    ├── __init__.py
    ├── file_tools.py            # create_file handler
    ├── code_tools.py            # write_code handler
    └── text_tools.py            # summarize_text handler
```
