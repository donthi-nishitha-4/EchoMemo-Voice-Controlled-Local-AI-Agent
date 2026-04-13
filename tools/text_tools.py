import ollama


def summarize_text(text: str) -> str:
    """
    Summarize the provided text using the local LLM via Ollama.
    Returns a clean 5-line summary.
    """
    prompt = f"""Summarize the following text clearly in exactly 5 bullet points.
Return ONLY the bullet points. No preamble, no intro sentence.

Text:
{text}"""

    try:
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"Summarization error: {str(e)}"
