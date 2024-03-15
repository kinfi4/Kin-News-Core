from typing import Any, Optional
from datetime import datetime

from pydantic import field_validator, ConfigDict, BaseModel, Field, field_serializer

from kin_txt_core.constants import DEFAULT_DATETIME_FORMAT
from kin_txt_core.types.reports import (
    VisualizationDiagramTypes,
    RawContentTypes,
    DataByCategory,
    DataByDateChannelCategory,
)
from kin_txt_core.reports_building.constants import (
    ReportProcessingResult,
    ReportTypes,
)


class BaseReport(BaseModel):
    report_id: int = Field(..., alias="reportId")
    name: str = Field(max_length=80, alias="name")
    report_type: ReportTypes = Field(ReportTypes.STATISTICAL, alias="reportType")
    processing_status: ReportProcessingResult = Field(..., alias="processingStatus")
    generation_date: datetime = Field(..., alias="generationDate")

    report_failed_reason: str | None = Field(None, alias="reportFailedReason")
    report_warnings: list[str] | None = Field(None, alias="reportWarnings")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("generation_date", mode="before")
    def parse_generation_date(cls, value: str | datetime) -> datetime:
        if isinstance(value, str):  # in case if passed value was string case to datetime
            return datetime.strptime(value, DEFAULT_DATETIME_FORMAT)

        return value

    @field_serializer("generation_date", when_used="json")
    @staticmethod
    def serialize_generation_date(value: datetime, _info) -> str:
        return value.strftime(DEFAULT_DATETIME_FORMAT)


class StatisticalReport(BaseReport):
    posts_categories: list[str] | None = Field(None, alias="postsCategories")
    visualization_diagrams_list: list[VisualizationDiagramTypes] | None = Field(None, alias="visualizationDiagramsList")

    total_messages_count: int | None = Field(None, alias="totalMessagesCount")

    data: dict[RawContentTypes, DataByCategory | DataByDateChannelCategory] | None = Field(None, alias="data")
    model_config = ConfigDict(populate_by_name=True)


class WordCloudReport(BaseReport):
    posts_categories: list[str] | None = Field(None, alias="postsCategories")

    total_words: int | None = Field(None, alias="totalWords")
    total_words_frequency: list[tuple[str, int]] | None = Field(None, alias="totalWordsFrequency")
    data_by_channel: dict[str, list[tuple[str, int]]] | None = Field(None, alias="dataByChannel")

    data_by_category: Optional[
        dict[str, list[tuple[str, int]]]
    ] = Field(None, alias="dataByCategory")

    data_by_channel_by_category: Optional[
        dict[str, dict[str, list[tuple[str, int]]]]
    ] = Field(None, alias="dataByChannelByCategory")

    model_config = ConfigDict(populate_by_name=True)
