"""
Transcript Text Cleaner Utility
Authored by @Arijit Dutta
"""
import re

def clean_transcript_text(text: str) -> str:
    """Clean transcript artifacts such as music cues, noise tags, and whitespace."""
    if not text:
        return ""
    # Remove bracketed tags like [Music], [Applause], (laughter)
    cleaned = re.sub(r'\[.*?\]|\(.*?\)', '', text)
    # Normalize multiple whitespaces and newlines
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned
