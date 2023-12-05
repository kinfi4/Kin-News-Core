from typing import Any


def pydantic_errors_prettifier(errors: list[dict[str, Any]]) -> list[str]:
    prettified_errors = []

    for error_dict in errors:
        error_fields = error_dict.get("loc")

        if len(error_fields) > 1:
            error_fields_string = "Fields " + ", ".join(error_fields)
        else:
            error_fields_string = error_fields[0] if error_fields[0] != "__root__" else "Sorry, but"

        error_msg = error_dict.get("msg")

        prettified_errors.append(f"{error_fields_string}: {error_msg}")

    return prettified_errors
