import re
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def _extract_filename(transcription: str) -> str:
    """Try to extract a filename from the transcription."""
    # Match patterns like "called notes", "named todo", "file called report.txt"
    match = re.search(r"(?:called|named|file\s+(?:called|named)?)\s+([\w\-]+(?:\.\w+)?)",
                      transcription.lower())
    if match:
        name = match.group(1)
        # Add .txt extension if no extension found
        if "." not in name:
            name += ".txt"
        return name

    # Fallback: timestamp-based name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"new_file_{timestamp}.txt"


def create_file_from_text(transcription: str) -> str:
    """
    Create a file in the output/ folder based on the user's voice request.
    Attempts to extract a filename from the transcription.
    Writes the transcription as the initial content of the file.
    """
    filename = _extract_filename(transcription)
    file_path = OUTPUT_DIR / filename

    # Write the transcription as starter content (not just an empty touch)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"Created by Voice AI Agent\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Voice command: {transcription}\n")

    return f"✅ File created: `{file_path}`"
