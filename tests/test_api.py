import pytest
from fastapi import HTTPException

from api.main import health, root, transactions, transactions_summary


def test_health():
    result = health()

    assert result["status"] == "ok"
    assert "timestamp" in result


def test_root():
    result = root()

    assert result["service"] == "reto-sysops-api"
    assert result["status"] == "running"


def test_transactions_invalid_limit():
    with pytest.raises(HTTPException) as exc:
        transactions(0)

    assert exc.value.status_code == 400


def test_transactions(monkeypatch):
    mock_data = [
        {
            "event_id": "evt-001",
            "status": "approved"
        }
    ]

    monkeypatch.setattr(
        "api.main.execute_query",
        lambda query: mock_data
    )

    result = transactions(10)

    assert result["count"] == 1
    assert len(result["data"]) == 1
    assert result["data"][0]["event_id"] == "evt-001"


def test_transactions_summary(monkeypatch):
    mock_data = [
        {
            "status": "approved",
            "total_transactions": "14"
        },
        {
            "status": "rejected",
            "total_transactions": "6"
        }
    ]

    monkeypatch.setattr(
        "api.main.execute_query",
        lambda query: mock_data
    )

    result = transactions_summary()

    assert len(result["data"]) == 2
    assert result["data"][0]["status"] == "approved"
