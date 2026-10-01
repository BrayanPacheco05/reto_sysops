import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUTPUT_DIR = Path("data/sample")
OUTPUT_FILE = OUTPUT_DIR / "transactions.json"

USERS = [f"user-{i:03d}" for i in range(1, 21)]
PAYMENT_METHODS = ["card", "transfer", "cash"]
CURRENCIES = ["MXN"]


def generate_transaction():
    timestamp = datetime.now(timezone.utc) - timedelta(
        minutes=random.randint(0, 1440)
    )

    status = random.choices(
        ["approved", "rejected"],
        weights=[75, 25]
    )[0]

    return {
        "event_id": f"evt-{uuid.uuid4().hex}",
        "timestamp": timestamp.isoformat(),
        "user_id": random.choice(USERS),
        "transaction_id": f"txn-{uuid.uuid4().hex[:12]}",
        "amount": round(random.uniform(100, 5000), 2),
        "currency": random.choice(CURRENCIES),
        "status": status,
        "payment_method": random.choice(PAYMENT_METHODS)
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    events = [
        generate_transaction()
        for _ in range(100)
    ]

    with open(OUTPUT_FILE, "w") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

    print(f"Generated {len(events)} transactions")
    print(f"File: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
