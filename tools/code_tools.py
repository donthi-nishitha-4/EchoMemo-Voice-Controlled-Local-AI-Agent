import re
from pathlib import Path
import ollama

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def _extract_filename(user_request: str) -> str:
    """Try to extract a meaningful filename from the user's request."""
    # Look for explicit filename mentions like "called retry.py" or "named helpers.py"
    match = re.search(r"(?:called|named|file|save\s+(?:it\s+)?(?:as|to))\s+([\w\-]+(?:\.py)?)", 
                      user_request.lower())
    if match:
        name = match.group(1)
        if not name.endswith(".py"):
            name += ".py"
        return name

    # Otherwise derive from first meaningful noun/verb in the request
    words = re.findall(r"\b[a-z]{4,}\b", user_request.lower())
    skip = {"write", "create", "make", "with", "that", "this", "code", "python",
            "function", "script", "file", "please", "generate", "using"}
    for word in words:
        if word not in skip:
            return f"{word}.py"

    return "generated_code.py"


def _strip_markdown(code: str) -> str:
    """Remove ```python ... ``` or ``` ... ``` fences that LLMs often wrap code in."""
    # Remove opening fence (with optional language tag)
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    # Remove closing fence
    code = re.sub(r"\n?```$", "", code.strip())
    return code.strip()


def generate_code_file(filename: str, user_request: str):
    """
    Generate Python code from a user request using the local LLM,
    then save it to the output/ folder.

    Returns: (file_path, clean_code)
    """
    # Let the LLM pick a better filename if we got a generic one
    if filename == "generated_code.py":
        filename = _extract_filename(user_request)

    prompt = f"""Write clean, well-commented Python code for the following request.
Return ONLY the raw Python code. Do NOT include any explanation, markdown formatting, or code fences.

Request: {user_request}"""

    try:
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        raw_code = response["message"]["content"]
    except Exception as e:
        raw_code = f"# Error generating code: {str(e)}\n"

    clean_code = _strip_markdown(raw_code)

    file_path = OUTPUT_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(clean_code)

    return file_path, clean_code
