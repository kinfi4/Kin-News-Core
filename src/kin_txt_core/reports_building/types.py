from typing import TypeAlias, Protocol


CategoryMapping: TypeAlias = dict[str, str]
ValidationResult: TypeAlias = tuple[bool, str | None]


class Validator(Protocol):
    def __init__(self, path: str) -> None:
        ...

    def validate_model(self, model_entity: "ModelEntity") -> None:
        ...
