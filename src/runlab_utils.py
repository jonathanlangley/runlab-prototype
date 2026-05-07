from __future__ import annotations

from html import escape


def html_text(value: object) -> str:
    return escape(str(value or ""))


def safe_get(item: object, key: str, default: object = "") -> object:
    if isinstance(item, dict):
        return item.get(key, default)
    return default


def normalise_label_value(item: object) -> tuple[str, str]:
    if isinstance(item, dict):
        return str(item.get("label", item.get("title", "Metric"))), str(
            item.get("value", item.get("detail", ""))
        )

    if isinstance(item, (list, tuple)) and len(item) >= 2:
        return str(item[0]), str(item[1])

    return "Metric", str(item)


def normalise_signal(item: object) -> dict:
    if isinstance(item, dict):
        return {
            "title": str(item.get("title", item.get("label", "Signal"))),
            "detail": str(item.get("detail", item.get("value", ""))),
            "priority": str(item.get("priority", "")),
        }

    if isinstance(item, (list, tuple)):
        title = str(item[0]) if len(item) > 0 else "Signal"
        detail = str(item[1]) if len(item) > 1 else ""
        priority = str(item[2]) if len(item) > 2 else ""
        return {"title": title, "detail": detail, "priority": priority}

    return {"title": "Signal", "detail": str(item), "priority": ""}


def parse_time_to_seconds(value: str) -> int | None:
    try:
        parts = value.strip().split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except Exception:
        return None

    return None


def seconds_to_pace_str(seconds_per_km: float | None) -> str:
    if seconds_per_km is None:
        return "N/A"

    seconds = int(round(seconds_per_km))
    return f"{seconds // 60}:{seconds % 60:02d}/km"
