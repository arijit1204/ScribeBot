"""
YouTube Transcript and Channel Ingestion Loader
Authored by @Arijit Dutta
"""
import re
import requests
from typing import List
from html import unescape
from langchain_core.documents import Document
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

SUPPORTED_LANGUAGES = [
    'en', 'hi', 'en-US', 'hi-IN', 'es', 'fr', 'de', 
    'it', 'pt', 'ru', 'ja', 'ko', 'zh-Hans', 'zh-Hant'
]

def get_browser_session() -> requests.Session:
    """Create requests.Session with realistic desktop browser headers to prevent YouTube IP blocks."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none'
    })
    return session

def extract_video_id(youtube_url: str) -> str:
    """Extract 11-character YouTube video ID from standard or shortened URL."""
    video_id_match = re.search(r'(?:v=|\/|embed\/|youtu\.be\/)([0-9A-Za-z_-]{11})', youtube_url)
    if not video_id_match:
        raise ValueError("Invalid YouTube URL format. Please provide a valid YouTube video link.")
    return video_id_match.group(1)

def load_youtube_transcript(youtube_url: str) -> List[Document]:
    """
    Fetch transcript for a given YouTube URL with multi-tier browser session fallback
    and multi-language support.
    """
    video_id = extract_video_id(youtube_url)
    session = get_browser_session()
    
    # Method 1: YouTubeTranscriptApi with custom browser HTTP Session
    try:
        api = YouTubeTranscriptApi(http_client=session)
        transcript_list = api.list(video_id)
        
        # Try finding transcript in preferred languages first
        target_transcript = None
        try:
            target_transcript = transcript_list.find_transcript(SUPPORTED_LANGUAGES)
        except (NoTranscriptFound, Exception):
            # Fall back to first available transcript (manual or auto-generated)
            target_transcript = next(iter(transcript_list))
            
        if target_transcript:
            fetched_data = target_transcript.fetch()
            full_text = " ".join([snippet.text for snippet in fetched_data])
            if full_text.strip():
                return [Document(
                    page_content=full_text,
                    metadata={"source": youtube_url, "video_id": video_id, "language": target_transcript.language_code}
                )]
    except TranscriptsDisabled:
        raise RuntimeError("Subtitles/Transcripts are disabled for this YouTube video.")
    except Exception as e:
        print(f"[Loader Notice] Primary session fetch info: {e}")

    # Method 2: Standard LangChain YoutubeLoader fallback
    try:
        from langchain_community.document_loaders import YoutubeLoader
        loader = YoutubeLoader.from_youtube_url(
            youtube_url,
            add_video_info=False,
            language=SUPPORTED_LANGUAGES
        )
        docs = loader.load()
        if docs and docs[0].page_content.strip():
            for doc in docs:
                doc.metadata["video_id"] = video_id
                doc.metadata["source"] = youtube_url
            return docs
    except Exception as e:
        print(f"[Loader Notice] LangChain YoutubeLoader fallback info: {e}")

    raise RuntimeError(f"Could not retrieve transcript for YouTube video ({video_id}). Please verify the video has captions enabled.")
