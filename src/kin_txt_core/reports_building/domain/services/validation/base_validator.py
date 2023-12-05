from kin_txt_core.reports_building.domain.entities import ModelEntity
from kin_txt_core.reports_building.types import ValidationResult

__all__ = ["BaseValidator"]


class BaseValidator:
    def validate_model(self, _: ModelEntity) -> ValidationResult:
        return True, None
