import re
from enum import Enum, EnumMeta
from typing import Type

REPORTS_BUILDER_EXCHANGE = "ReportsBuilder"
REPORTS_STORING_EXCHANGE = "ReportsStoring"
MODEL_TYPES_EXCHANGE = "ModelTypes"


class ReportTypes(str, Enum):
    STATISTICAL = "Statistical"
    WORD_CLOUD = "WordCloud"


class ReportProcessingResult(str, Enum):
    POSTPONED = "Postponed"
    READY = "Ready"
    PROCESSING = "Processing"


class ModelStatuses(str, Enum):
    VALIDATED = "Validated"
    VALIDATION_FAILED = "ValidationFailed"
    VALIDATING = "Validating"
    CREATED = "Created"


class ModelTypes(str, Enum):
    SKLEARN = "Sklearn Model"
    KERAS = "Keras Model"
    CUSTOM = "Custom Model"