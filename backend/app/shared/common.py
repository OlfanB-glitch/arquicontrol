from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def generate_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def create_audit_fields() -> dict:
    timestamp = utc_now_iso()
    return {
        "id": generate_id(),
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }


def touch_updated_at(document: dict) -> dict:
    updated = dict(document)
    updated["updatedAt"] = utc_now_iso()
    return updated


def safe_filename(filename: str) -> str:
    path = Path(filename)
    stem = path.stem.replace(" ", "-")
    return f"{stem}-{uuid4().hex[:8]}{path.suffix.lower()}"


def sum_amount(items: list[dict], field_name: str) -> float:
    return round(sum(float(item.get(field_name, 0) or 0) for item in items), 2)