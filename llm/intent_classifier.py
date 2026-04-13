import re
import ollama

# All valid intents the system supports
VALID_INTENTS = {"create_file", "write_code", "summarize_text", "general_chat"}


def classify_intent(text: str) -> str:
    """
    Use a local LLM (via Ollama) to classify the user's intent from transcribed text.
    Returns one of: create_file | write_code | summarize_text | general_chat
    """
    prompt = f"""You are an intent classifier. Classify the user's request into EXACTLY one of these intents:
- create_file
- write_code
- summarize_text
- general_chat

Rules:
- "create_file" → user wants to create a file or folder
- "write_code" → user wants code generated and saved (e.g. "write a function", "create a Python script")
- "summarize_text" → user wants a summary of something
- "general_chat" → anything else (questions, conversation, etc.)

Respond with ONLY the intent name. No explanation. No punctuation. No numbering.

User request: {text}

Intent:"""

    try:
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response["message"]["content"].strip().lower()
    except Exception as e:
        print(f"[Intent Classifier] Ollama error: {e}")
        return "general_chat"

    return _normalize_intent(raw)


def _normalize_intent(raw: str) -> str:
    """
    Robustly map any freeform LLM reply to a valid intent label.
    Handles cases like '2. write_code', 'The intent is write_code', 'WRITE_CODE', etc.
    """
    # Direct match first
    cleaned = raw.strip().strip("\"'").replace("-", "_").replace(" ", "_")
    if cleaned in VALID_INTENTS:
        return cleaned

    # Scan for any valid intent keyword inside the reply
    for intent in VALID_INTENTS:
        if intent in raw:
            return intent

    # Fuzzy keyword fallback
    if any(w in raw for w in ["file", "folder", "creat", "touch", "new file"]):
        return "create_file"
    if any(w in raw for w in ["code", "script", "function", "program", "write", "python", "generat"]):
        return "write_code"
    if any(w in raw for w in ["summar", "brief", "shorten", "condense", "tldr"]):
        return "summarize_text"

    return "general_chat"
