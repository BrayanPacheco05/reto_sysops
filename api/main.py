from datetime import datetime, timezone
import time

import boto3
from fastapi import FastAPI, HTTPException


REGION = "us-east-1"
DATABASE = "reto_sysops_dev_catalog"
TABLE = "transactions"
WORKGROUP = "reto-sysops-dev-workgroup"

athena = boto3.client("athena", region_name=REGION)

app = FastAPI(
    title="Reto SysOps API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/")
def root():
    return {
        "service": "reto-sysops-api",
        "status": "running"
    }


def execute_query(query: str):
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            "Database": DATABASE
        },
        WorkGroup=WORKGROUP
    )

    query_id = response["QueryExecutionId"]

    for _ in range(30):
        result = athena.get_query_execution(
            QueryExecutionId=query_id
        )

        status = result["QueryExecution"]["Status"]["State"]

        if status == "SUCCEEDED":
            break

        if status in ["FAILED", "CANCELLED"]:
            reason = result["QueryExecution"]["Status"].get(
                "StateChangeReason",
                "Unknown error"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Athena query failed: {reason}"
            )

        time.sleep(1)

    else:
        raise HTTPException(
            status_code=504,
            detail="Athena query timeout"
        )

    response = athena.get_query_results(
        QueryExecutionId=query_id
    )

    rows = response["ResultSet"]["Rows"]

    if not rows:
        return []

    headers = [
        column.get("VarCharValue")
        for column in rows[0]["Data"]
    ]

    data = []

    for row in rows[1:]:
        values = [
            column.get("VarCharValue")
            for column in row["Data"]
        ]

        item = dict(zip(headers, values))
        data.append(item)

    return data


@app.get("/transactions")
def transactions(limit: int = 10):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100"
        )

    query = f"""
        SELECT
            event_id,
            timestamp,
            user_id,
            transaction_id,
            amount,
            currency,
            status,
            payment_method
        FROM {TABLE}
        ORDER BY timestamp DESC
        LIMIT {limit}
    """

    results = execute_query(query)

    return {
        "count": len(results),
        "data": results
    }
@app.get("/transactions/summary")
def transactions_summary():
    query = f"""
        SELECT
            status,
            COUNT(*) AS total_transactions,
            ROUND(SUM(amount), 2) AS total_amount,
            ROUND(AVG(amount), 2) AS average_amount
        FROM {TABLE}
        GROUP BY status
        ORDER BY total_transactions DESC
    """

    results = execute_query(query)

    return {
        "data": results
    }
