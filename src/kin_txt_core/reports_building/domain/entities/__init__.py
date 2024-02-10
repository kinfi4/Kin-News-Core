from typing import Any

from pydantic import model_validator, ConfigDict, BaseModel

from .preprocessing import PreprocessingConfig
from .generate_report import GenerateReportEntity
from .reports import BaseReport, WordCloudReport, StatisticalReport
from .model import ModelEntity, ModelValidationEntity, CustomModelRegistrationEntity
from .visualization_template import VisualizationTemplate

from kin_txt_core.reports_building.domain.services.predicting.predictor.interface import IPredictor
from kin_txt_core.reports_building.constants import ReportTypes


class GenerationTemplateWrapper(BaseModel):
    generate_report_metadata: GenerateReportEntity
    model_metadata: ModelEntity
    predictor: IPredictor
    visualization_template: VisualizationTemplate | None = None

    @model_validator()
    @classmethod
    def validate_start_and_end_dates_difference(cls, fields: dict[str, Any]) -> dict[str, Any]:
        if fields["generate_report_metadata"].report_type == ReportTypes.STATISTICAL and fields["generate_report_metadata"].template_id is None:
            raise ValueError("Template id must be specified for statistical report type.")

        return fields
    model_config = ConfigDict(arbitrary_types_allowed=True)
