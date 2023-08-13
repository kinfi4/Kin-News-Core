from enum import Enum
from typing import Type, TypeAlias


DataByCategory: TypeAlias = dict[str, int]
DataByDateChannelCategory: TypeAlias = dict[str, DataByCategory]


class RawContentTypes(str, Enum):
    BY_DATE_BY_CATEGORY = "ByDateByCategory"
    BY_CHANNEL_BY_CATEGORY = "ByChannelByCategory"
    BY_CATEGORY = "ByCategory"
    BY_CHANNEL = "ByChannel"
    BY_DATE = "ByDate"
    BY_DAY_HOUR = "ByHour"
    BY_DATE_BY_CHANNEL = "ByDateByChannel"


class DiagramTypes(str, Enum):
    PIE = "Pie"
    BAR = "Bar"
    STACKED_BAR = "StackedBar"
    LINE = "Line"
    MULTI_LINE = "MultiLine"
    TWO_LEVEL_PIE = "TwoLevelPie"
    AREA = "Area"
    MULTI_AREA = "MultiArea"
    RADAR = "Radar"


class VisualizationDiagramTypes(str, Enum):
    BY_CATEGORY__PIE = f"{RawContentTypes.BY_CATEGORY}__{DiagramTypes.PIE}"
    BY_CHANNEL__PIE = f"{RawContentTypes.BY_CHANNEL}__{DiagramTypes.PIE}"
    BY_CHANNEL_PLUS_BY_CATEGORY__PIE = f"{RawContentTypes.BY_CHANNEL}+{RawContentTypes.BY_CATEGORY}__{DiagramTypes.TWO_LEVEL_PIE}"

    BY_CATEGORY__BAR = f"{RawContentTypes.BY_CATEGORY}__{DiagramTypes.BAR}"
    BY_CHANNEL__BAR = f"{RawContentTypes.BY_CHANNEL}__{DiagramTypes.BAR}"
    BY_HOUR__BAR = f"{RawContentTypes.BY_DAY_HOUR}__{DiagramTypes.BAR}"
    BY_CHANNEL_BY_CATEGORY_STACKED_BAR = f"{RawContentTypes.BY_CHANNEL_BY_CATEGORY}__{DiagramTypes.STACKED_BAR}"

    BY_DATE_LINE = f"{RawContentTypes.BY_DATE}__{DiagramTypes.LINE}"
    BY_DATE_BY_CATEGORY_MULTI_LINE = f"{RawContentTypes.BY_DATE_BY_CATEGORY}__{DiagramTypes.MULTI_LINE}"
    BY_DATE_BY_CHANNEL_MULTI_LINE = f"{RawContentTypes.BY_DATE_BY_CHANNEL}__{DiagramTypes.MULTI_LINE}"

    BY_DATE_BY_CATEGORY_MULTI_AREA = f"{RawContentTypes.BY_DATE_BY_CATEGORY}__{DiagramTypes.MULTI_AREA}"

    BY_CATEGORY_RADAR = f"{RawContentTypes.BY_CATEGORY}__{DiagramTypes.RADAR}"
