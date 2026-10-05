import json
from typing import Any


def json_text(value: Any) -> str:
    return json.dumps(value, default=str, ensure_ascii=False)


def result_payload(value: Any) -> dict:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value
