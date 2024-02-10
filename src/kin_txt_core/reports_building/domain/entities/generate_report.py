from datetime import date, datetime

from pydantic import ConfigDict, BaseModel, field_validator

from kin_txt_core.reports_building.constants import ReportTypes, ModelTypes
from kin_txt_core.constants import DEFAULT_DATE_FORMAT
from kin_txt_core.datasources.constants import DataSourceTypes


def _cast_string_to_date(date_string: str) -> date:
    try:
        return datetime.strptime(date_string, DEFAULT_DATE_FORMAT).date()
    except ValueError:
        raise ValueError('Invalid string format for incoming StartDate field!')


class GenerateReportEntity(BaseModel):
    name: str
    username: str
    report_id: int
    model_code: str
    template_id: str
    start_date: date
    end_date: date
    channel_list: list[str]
    datasource_type: DataSourceTypes = DataSourceTypes.TELEGRAM
    model_type: ModelTypes
    report_type: ReportTypes | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("start_date", "end_date", mode="before")
    def validate_and_cast_start_date(cls, value: str | date) -> date:
        if isinstance(value, str):
            return _cast_string_to_date(value)

        return value
