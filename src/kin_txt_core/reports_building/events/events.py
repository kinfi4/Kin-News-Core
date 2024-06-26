from kin_txt_core.messaging.dtos.event import BasicEvent

from kin_txt_core.reports_building.domain.entities import (
    StatisticalReport,
    WordCloudReport,
    GenerateReportEntity,
    BaseReport,
    ModelEntity,
    CustomModelRegistrationEntity,
)


class GenerateReportRequestOccurred(BasicEvent, GenerateReportEntity):
    pass


class ReportProcessingStarted(BasicEvent):
    report_id: int


class ReportProcessingFailed(BasicEvent, BaseReport):
    username: str


class WordCloudReportProcessingFinished(BasicEvent, WordCloudReport):
    username: str


class StatisticalReportProcessingFinished(BasicEvent, StatisticalReport):
    username: str


class ModelValidationRequestOccurred(BasicEvent, ModelEntity):
    pass


class ModelValidationStarted(BasicEvent):
    code: str
    username: str


class ModelValidationFinished(BasicEvent):
    code: str
    username: str
    validation_passed: bool
    message: str | None = None


class ReportsBuilderCreated(BasicEvent, CustomModelRegistrationEntity):
    pass
