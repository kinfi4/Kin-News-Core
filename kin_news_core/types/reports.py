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
    BY_DAY_HOUR = "ByDayHour"
    BY_DATE_BY_CHANNEL = "ByDateByChannel"


class DiagramTypes(str, Enum):
    PIE = "Pie"
    BAR = "Bar"
    LINE = "Line"
    HISTOGRAM = "Histogram"
    SCATTER = "Scatter"
    HEATMAP = "Heatmap"


def generate_visualization_diagram_types() -> Type[Enum]:
    enum_dict = {f'{rc}__{dt}': f'{rc}__{dt}' for rc in RawContentTypes for dt in DiagramTypes}

    _VisualizationDiagramTypes = Enum("VisualizationDiagramTypes", enum_dict)

    # Add a __str__ method to the Enum
    def enum_str(self):
        return self.value

    _VisualizationDiagramTypes.__str__ = enum_str
    return _VisualizationDiagramTypes


VisualizationDiagramTypes = generate_visualization_diagram_types()
