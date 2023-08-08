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
    LINE = "Line"
    HISTOGRAM = "Histogram"
    SCATTER = "Scatter"
    HEATMAP = "Heatmap"
    TWO_LEVEL_PIE = "TwoLevelPie"
    AREA = "Area"


class VisualizationDiagramTypes(str, Enum):
    BY_CATEGORY__PIE = f"{RawContentTypes.BY_CATEGORY}__{DiagramTypes.PIE}"
    BY_CATEGORY__BAR = f"{RawContentTypes.BY_CATEGORY}__{DiagramTypes.BAR}"
    BY_CATEGORY__LINE = f"{RawContentTypes.BY_CATEGORY}__{DiagramTypes.LINE}"

    BY_CHANNEL__PIE = f"{RawContentTypes.BY_CHANNEL}__{DiagramTypes.PIE}"
    BY_CHANNEL__BAR = f"{RawContentTypes.BY_CHANNEL}__{DiagramTypes.BAR}"

    BY_CHANNEL_PLUS_BY_CATEGORY__PIE = f"{RawContentTypes.BY_CHANNEL}+{RawContentTypes.BY_CATEGORY}__{DiagramTypes.TWO_LEVEL_PIE}"

    BY_HOUR__BAR = f"{RawContentTypes.BY_DAY_HOUR}__{DiagramTypes.BAR}"

    BY_DATE_LINE = f"{RawContentTypes.BY_DATE}__{DiagramTypes.LINE}"
