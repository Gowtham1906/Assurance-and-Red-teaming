"""D01 - Schema and format validity (HARD gate).

Spec (plan §6):
    Implementation : pydantic or JSON Schema on output and tool-call arguments.
    Pass criterion : 100% valid.
    OWASP          : LLM05 (improper output handling), LLM01 (agent args).

Supports two schema styles:
  * a pydantic BaseModel subclass  -> validated via model_validate
  * a dict JSON-Schema subset      -> {"type","required","properties"} checked
"""

from __future__ import annotations

from typing import Any

from assure_core.result import CheckResult, failed_result, passed_result

_JSON_TYPES = {
    "object": dict, "array": list, "string": str,
    "number": (int, float), "integer": int, "boolean": bool,
}


def _validate_json_schema(output: Any, schema: dict) -> list[str]:
    """Minimal JSON-Schema subset validator. Returns a list of error strings."""
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        py = _JSON_TYPES.get(expected)
        if py and not isinstance(output, py):
            errors.append(f"expected type '{expected}', got {type(output).__name__}")
            return errors
    if schema.get("type") == "object" and isinstance(output, dict):
        for key in schema.get("required", []):
            if key not in output:
                errors.append(f"missing required field '{key}'")
        for key, subschema in schema.get("properties", {}).items():
            if key in output and isinstance(subschema, dict):
                errors.extend(
                    f"{key}: {e}" for e in _validate_json_schema(output[key], subschema)
                )
    return errors


def check_schema(output: Any, schema: Any) -> CheckResult:
    """Validate output against a pydantic model or a JSON-Schema dict."""
    # pydantic model?
    if hasattr(schema, "model_validate"):
        try:
            schema.model_validate(output)
            return passed_result("D01")
        except Exception as exc:  # pydantic ValidationError or others
            return failed_result("D01", "schema validation failed", error=str(exc))

    if isinstance(schema, dict):
        errors = _validate_json_schema(output, schema)
        if errors:
            return failed_result("D01", "schema validation failed", errors=errors)
        return passed_result("D01")

    return failed_result("D01", "unsupported schema type", schema_type=str(type(schema)))
