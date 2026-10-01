import json
import random
import uuid
from datetime import datetime, timezone

import boto3


REGION = "us-east-1"
BUCKET = "reto-sysops-dev-data-39fff1603228afc5d2b368f9d1"

s3 = boto3.client("s3", region_name=REGION)


def generate_event():
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": f"user-{random.randint(1, 100)}",
        "transaction_id": f"txn-{uuid.uuid4().hex[:12]}",
        "amount": round(random.uniform(50, 5000), 2),
        "currency": "MXN",
        "status": random.choice(["approved", "approved", "approved", "rejected"]),
        "payment_method": random.choice(["card", "transfer", "cash"])
    }


def main():
    events = [generate_event() for _ in range(20)]

    now = datetime.now(timezone.utc)

    key = (
        f"bronze/year={now.year}/"
        f"month={now.month:02d}/"
        f"day={now.day:02d}/"
        f"events-{now.strftime('%H%M%S')}.json"
    )

    body = "\n".join(json.dumps(event) for event in events)

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/json"
    )

    print(f"Uploaded {len(events)} events")
    print(f"s3://{BUCKET}/{key}")


if __name__ == "__main__":
    main()
