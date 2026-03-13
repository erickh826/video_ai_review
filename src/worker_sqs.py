



import json
import os
import time
import urllib.parse

import boto3

try:
    # Works when run from the project root, e.g. `python -m src.worker_sqs`.
    from src.config import settings
except ModuleNotFoundError:
    # Works when run directly from inside the `src` folder.
    from config import settings

AWS_REGION = settings.aws_region or "us-east-1"
SQS_QUEUE_URL = settings.sqs_queue_url



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

    # direct S3->SQS
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


def main():
    sqs = boto3.client("sqs", region_name=AWS_REGION)
    s3 = boto3.client("s3", region_name=AWS_REGION)

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

        # --- Workflow 03 minimal step: verify object exists (no download) ---
        head = s3.head_object(Bucket=bucket, Key=key)
        size = head.get("ContentLength")
        etag = head.get("ETag")

        print(
            f"[JOB] bucket={bucket} key={key} video_id={video_id} "
            f"exists=true size={size} etag={etag}"
        )

        # POC: delete immediately once parsed + verified
        sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt)
        print("[OK] deleted message")

        time.sleep(0.2)


if __name__ == "__main__":
    main()