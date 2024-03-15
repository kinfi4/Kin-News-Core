from typing import Any

from pydantic import model_validator, ConfigDict, BaseModel

from .preprocessing import PreprocessingConfig
from .generate_report import GenerateReportEntity
from .reports import BaseReport, WordCloudReport, StatisticalReport
from .model import ModelEntity, ModelValidationEntity, CustomModelRegistrationEntity
from .visualization_template import VisualizationTemplate
