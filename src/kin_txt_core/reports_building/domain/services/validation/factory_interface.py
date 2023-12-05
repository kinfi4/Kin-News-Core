from kin_txt_core.reports_building.domain.entities import ModelEntity
from kin_txt_core.reports_building.domain.services.validation.base_validator import BaseValidator

__all__ = ["BaseValidatorFactory"]


class BaseValidatorFactory:
    def create_validator(self, _: ModelEntity) -> BaseValidator:
        return BaseValidator()
