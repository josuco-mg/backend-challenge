from typing import Any, Dict, Sequence

from pydantic import ValidationError


def parsed_validation_error(exception: ValidationError) -> Dict[str, Any]:
    drf_data: Dict[str, Any] = {}
    for error in exception.errors():
        _set_nested(drf_data, error["loc"], [error["msg"]])
    return drf_data


def _set_nested(data: Dict[str, Any], keys: Sequence[str], value: Any) -> None:
    for key in keys[:-1]:
        data = data.setdefault(str(key), {})
    data[keys[-1]] = value
