import json
import os
import subprocess
import time
import urllib.parse
from pathlib import Path

import boto3

try:
    # Optional: if you use a .env file locally
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass


AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]
LOCAL_VIDEO_ROOT = os.environ["LOCAL_VIDEO_ROOT"]

# Optional; if not set, "ffmpeg" must be on PATH
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")


def _try_parse_s3_event(payload: dict):
    records = payload.get("Records", [])
    if not records:
        return None

    r0 = records[0]
    bucket = r0["s3"]["bucket"]["name"]
    key_encoded = r0["s3"]["object"]["key"]
    key = urllib.parse.unquote_plus(key_encoded)
    return bucket, key


def extract_s3_info_from_sqs_message(body: str):
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return None

    parsed = _try_parse_s3_event(payload)
    if parsed:
        return parsed

    # SNS wrapper (Message is a JSON string)
    msg = payload.get("Message")
    if isinstance(msg, str):
        try:
            inner = json.loads(msg)
        except json.JSONDecodeError:
            return None
        parsed = _try_parse_s3_event(inner)
        if parsed:
            return parsed

    return None


def parse_video_id_from_key(key: str) -> str:
    # expected: video-review/<video_id>/raw/<filename>.mp4
    parts = key.split("/")
    if len(parts) < 4:
        raise ValueError(f"Unexpected key format: {key}")
    if parts[0] != "video-review":
        raise ValueError(f"Unexpected prefix: {parts[0]}")
    return parts[1]


def local_path_from_s3_key(local_root: str, s3_key: str) -> Path:
    # S3 key uses "/" always; convert to OS path safely
    parts = [p for p in s3_key.split("/") if p]
    return Path(local_root, *parts)


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def extract_audio_wav(input_mp4: Path, output_wav: Path) -> None:
    """
    Extract mono 16k wav for STT.
    """
    ensure_parent_dir(output_wav)

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i",
        str(input_mp4),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(output_wav),
    ]

    # Capture output for debugging
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "ffmpeg failed\n"
            f"cmd: {' '.join(cmd)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
        )


def main():
    sqs = boto3.client("sqs", region_name=AWS_REGION)
    s3 = boto3.client("s3", region_name=AWS_REGION)

    print(f"AWS_REGION={AWS_REGION}")
    print(f"LOCAL_VIDEO_ROOT={LOCAL_VIDEO_ROOT}")
    print(f"FFMPEG_PATH={FFMPEG_PATH}")

    while True:
        resp = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
            VisibilityTimeout=120,
        )

        msgs = resp.get("Messages", [])
        if not msgs:
            print("No messages.")
            continue

        msg = msgs[0]
        receipt = msg["ReceiptHandle"]
        body = msg.get("Body", "")

        parsed = extract_s3_info_from_sqs_message(body)
        if not parsed:
            preview = body[:200].replace("\n", "\\n")
            print(f"[SKIP] Non-S3 message body preview: {preview}")
            sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt)
            print("[OK] deleted non-s3 message")
            continue

        bucket, key = parsed

        # POC guard: only accept raw mp4 uploads
        if "/raw/" not in key or not key.lower().endswith(".mp4"):
            print(f"[SKIP] Not a raw mp4 key: {key}")
            sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt)
            print("[OK] deleted non-raw message")
            continue

        video_id = parse_video_id_from_key(key)

        try:
            # Verify object exists in S3 (no download)
            head = s3.head_object(Bucket=bucket, Key=key)
            size = head.get("ContentLength")
            etag = head.get("ETag")
            print(
                f"[JOB] bucket={bucket} key={key} video_id={video_id} "
                f"exists=true size={size} etag={etag}"
            )

            # Map to local mp4 path
            local_mp4 = local_path_from_s3_key(LOCAL_VIDEO_ROOT, key)
            if not local_mp4.exists():
                raise FileNotFoundError(f"Local mp4 not found: {local_mp4}")

            # Output wav next to video, in an audio/ folder
            out_wav = Path(local_mp4.parent.parent, "audio", f"{local_mp4.stem}.wav")
            extract_audio_wav(local_mp4, out_wav)
            print(f"[OK] extracted wav: {out_wav}")

        except Exception as e:
            # POC choice: delete even if failed, to keep queue moving
            print(f"[ERR] {e}")
            sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt)
            print("[OK] deleted message after error (POC)")
            continue

        # POC: delete after successful processing
        sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt)
        print("[OK] deleted message")

        time.sleep(0.2)


if __name__ == "__main__":
    main()