import json
import io
import boto3
import pandas as pd


REGION = "us-east-1"
BUCKET = "reto-sysops-dev-data-39fff1603228afc5d2b368f9d1"

s3 = boto3.client("s3", region_name=REGION)


def get_bronze_files():
    response = s3.list_objects_v2(
        Bucket=BUCKET,
        Prefix="bronze/year="
    )

    return [
        obj["Key"]
        for obj in response.get("Contents", [])
        if obj["Key"].endswith(".json")
    ]


def read_events(keys):
    events = []

    for key in keys:
        response = s3.get_object(
            Bucket=BUCKET,
            Key=key
        )

        content = response["Body"].read().decode("utf-8")

        for line in content.splitlines():
            if line.strip():
                events.append(json.loads(line))

    return events


def transform(events):
    df = pd.DataFrame(events)

    required_columns = [
        "event_id",
        "timestamp",
        "user_id",
        "transaction_id",
        "amount",
        "currency",
        "status",
        "payment_method"
    ]

    df = df[required_columns]

    # Convertir tipos
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    # Eliminar registros inválidos
    df = df.dropna(
        subset=[
            "event_id",
            "timestamp",
            "user_id",
            "transaction_id",
            "amount"
        ]
    )

    # Eliminar duplicados
    df = df.drop_duplicates(
        subset=["event_id"]
    )

    return df


def upload_silver(df):
    buffer = io.BytesIO()

    df.to_parquet(
        buffer,
        index=False,
        engine="pyarrow"
    )

    buffer.seek(0)

    timestamp = pd.Timestamp.now("UTC")

    key = (
        f"silver/transactions/"
        f"year={timestamp.year}/"
        f"month={timestamp.month:02d}/"
        f"day={timestamp.day:02d}/"
        f"transactions.parquet"
    )

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=buffer.getvalue(),
        ContentType="application/octet-stream"
    )

    return key


def main():
    print("Starting Bronze -> Silver ETL")

    files = get_bronze_files()

    print(f"Bronze files found: {len(files)}")

    if not files:
        print("No Bronze files found.")
        return

    events = read_events(files)

    print(f"Events read: {len(events)}")

    df = transform(events)

    print(f"Valid events after cleaning: {len(df)}")

    key = upload_silver(df)

    print("Silver file uploaded:")
    print(f"s3://{BUCKET}/{key}")


if __name__ == "__main__":
    main()
