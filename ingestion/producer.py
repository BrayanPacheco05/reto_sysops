import json
from datetime import datetime, timezone
from pathlib import Path

import boto3


REGION = "us-east-1"
BUCKET = "reto-sysops-dev-data-39fff1603228afc5d2b368f9d1"

INPUT_FILE = Path("data/sample/transactions.json")

s3 = boto3.client("s3", region_name=REGION)


def read_events():
    with open(INPUT_FILE, "r") as file:
        events = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    return events


def upload_to_bronze(events):
    now = datetime.now(timezone.utc)

    key = (
        f"bronze/year={now.year}/"
        f"month={now.month:02d}/"
        f"day={now.day:02d}/"
        f"events-{now.strftime('%H%M%S')}.json"
    )

    body = "\n".join(
        json.dumps(event)
        for event in events
    )

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/json"
    )

    return key


def main():
    print("Starting synthetic event ingestion...")

    events = read_events()

    print(f"Events loaded: {len(events)}")

    key = upload_to_bronze(events)

    print("Bronze ingestion completed")
    print(f"Uploaded: {len(events)} events")
    print(f"s3://{BUCKET}/{key}")


if __name__ == "__main__":
    main()
