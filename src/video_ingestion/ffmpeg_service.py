"""
FFmpeg helpers for video processing tasks:
  - Thumbnail generation
  - HLS transcoding
  - Audio extraction (for STT pipeline — Workflow 03)
"""
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_thumbnail(input_path: str, output_path: str, timestamp: str = "00:00:01") -> str:
    """Extract a single JPEG thumbnail at the given timestamp."""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ss", timestamp,
        "-vframes", "1",
        "-q:v", "2",
        output_path,
    ]
    logger.info("Extracting thumbnail: %s -> %s", input_path, output_path)
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def generate_hls(input_path: str, output_dir: str) -> str:
    """Generate HLS playlist + segments. Returns path to master .m3u8."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    playlist = str(Path(output_dir) / "playlist.m3u8")
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-codec", "copy",
        "-start_number", "0",
        "-hls_time", "6",
        "-hls_list_size", "0",
        "-f", "hls",
        playlist,
    ]
    logger.info("Generating HLS: %s -> %s", input_path, output_dir)
    subprocess.run(cmd, check=True, capture_output=True)
    return playlist


def extract_audio(input_path: str, output_path: str) -> str:
    """Extract audio track as WAV (for STT pipeline)."""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_path,
    ]
    logger.info("Extracting audio: %s -> %s", input_path, output_path)
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def get_duration_seconds(input_path: str) -> int:
    """Probe video duration in seconds."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_path,
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return int(float(result.stdout.strip()))
