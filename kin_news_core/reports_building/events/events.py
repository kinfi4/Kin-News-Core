from kin_news_core.messaging.dtos.event import BasicEvent

from kin_news_core.reports_building.domain.entities import StatisticalReport, WordCloudReport, GenerateReportEntity, \
    BaseReport, ModelEntity


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
    error: str = None
