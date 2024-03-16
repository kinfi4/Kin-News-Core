import csv
import tempfile
from typing import Any, TextIO

from kin_txt_core.datasources.common.entities import ClassificationEntity
from kin_txt_core.exceptions import InvalidChannelURLError
from kin_txt_core.messaging import AbstractEventProducer
from kin_txt_core.constants import DEFAULT_DATE_FORMAT
from kin_txt_core.reports_building.domain.services.datasources.interface import IDataSourceFactory
from kin_txt_core.reports_building.domain.services.predicting.predictor import IPredictorFactory
from kin_txt_core.types.reports import RawContentTypes

from kin_txt_core.reports_building.domain.entities import (
    GenerateReportEntity,
    StatisticalReport,
    ModelEntity, WordCloudReport,
)
from kin_txt_core.reports_building.domain.entities.generation_template_wrapper import GenerationTemplateWrapper
from kin_txt_core.reports_building.domain.services.generate_report import IGeneratingReportsService
from kin_txt_core.reports_building.domain.services.statistical_report.reports_builder import StatisticalReportsBuilder
from kin_txt_core.reports_building.infrastructure.services import StatisticsService, ModelTypesService


class BuildStatisticalReportStrategy(IGeneratingReportsService):
    reports_builder = StatisticalReportsBuilder

    def __init__(
        self,
        events_producer: AbstractEventProducer,
        model_types_service: ModelTypesService,
        statistics_service: StatisticsService,
        predictor_factory: IPredictorFactory,
        datasource_factory: IDataSourceFactory,
    ) -> None:
        super().__init__(events_producer, model_types_service, predictor_factory, datasource_factory)
        self._statistics_service = statistics_service

        self._csv_writer = None

    def handle_posts(
        self,
        posts: list[ClassificationEntity],
        generate_report_wrapper: GenerationTemplateWrapper,
    ) -> dict[str, Any]:
        tmp_file = tempfile.NamedTemporaryFile()
        with open(tmp_file.name, "w") as user_report_file:
            self._csv_writer = csv.writer(user_report_file)
            self._csv_writer.writerow(["date", "channel", "hour", "text", "category"])

            handled_data = self._handle_posts(posts, generate_report_wrapper)

        with open(tmp_file.name, "r") as user_report_file:
            self._save_data_to_file(generate_report_wrapper.generate_report_metadata.report_id, user_report_file)
            
        return handled_data
    
    def _handle_posts(
        self,
        posts: list[ClassificationEntity],
        generate_report_wrapper: GenerationTemplateWrapper,
    ) -> dict[str, Any]:
        predictor = generate_report_wrapper.predictor
        posts_category_list = list(generate_report_wrapper.model_metadata.category_mapping.values())
        generate_report_meta = generate_report_wrapper.generate_report_metadata
        
        _data = self._initialize_report_data_dict(generate_report_wrapper)
        
        for message in posts:
            source_name = message.source_name
            message_date_str = message.created_at.date().strftime(DEFAULT_DATE_FORMAT)
            message_hour = message.created_at.hour

            message_category = predictor.predict(message)

            self._csv_writer.writerow([
                message_date_str,
                source_name,
                message_hour,
                message.text,
                message_category,
            ])

            _data["total_messages"] += 1

            for content_type in generate_report_wrapper.visualization_template.content_types:
                if content_type == RawContentTypes.BY_CHANNEL:
                    _data["data"][content_type][source_name] += 1
                elif content_type == RawContentTypes.BY_CATEGORY:
                    _data["data"][content_type][message_category] += 1
                elif content_type == RawContentTypes.BY_CHANNEL_BY_CATEGORY:
                    _data["data"][content_type][source_name][message_category] += 1
                elif content_type == RawContentTypes.BY_DAY_HOUR:
                    _data["data"][content_type][str(message_hour)] += 1
                elif content_type == RawContentTypes.BY_DATE:
                    if message_date_str not in _data["data"][content_type]:
                        _data["data"][content_type][message_date_str] = 0

                    _data["data"][content_type][message_date_str] += 1
                elif content_type == RawContentTypes.BY_DATE_BY_CATEGORY:
                    if message_date_str not in _data["data"][content_type]:
                        _data["data"][content_type][message_date_str] = {category: 0 for category in posts_category_list}

                    _data["data"][content_type][message_date_str][message_category] += 1
                elif content_type == RawContentTypes.BY_DATE_BY_CHANNEL:
                    if message_date_str not in _data["data"][content_type]:
                        _data["data"][content_type][message_date_str] = {
                            _channel: 0 for _channel in generate_report_meta.channel_list
                        }

                    _data["data"][content_type][message_date_str][source_name] += 1

        if RawContentTypes.BY_DATE_BY_CHANNEL in generate_report_wrapper.visualization_template.content_types:
            _data["data"][RawContentTypes.BY_DATE_BY_CHANNEL] = self._reverse_dict_keys(
                _data["data"][RawContentTypes.BY_DATE_BY_CHANNEL]
            )
        if RawContentTypes.BY_DATE_BY_CATEGORY in generate_report_wrapper.visualization_template.content_types:
            _data["data"][RawContentTypes.BY_DATE_BY_CATEGORY] = self._reverse_dict_keys(
                _data["data"][RawContentTypes.BY_DATE_BY_CATEGORY]
            )
        if RawContentTypes.BY_DATE in generate_report_wrapper.visualization_template.content_types:
            _data["data"][RawContentTypes.BY_DATE] = self._reverse_dict_keys(
                _data["data"][RawContentTypes.BY_DATE]
            )
            
        return _data

    def build_report(
        self,
        handled_data: dict[str, Any],
        generate_report_wrapper: GenerationTemplateWrapper,
    ) -> StatisticalReport:
        return (
            StatisticalReportsBuilder.from_report_id(generate_report_wrapper.generate_report_metadata.report_id)
            .set_visualization_diagrams_list(
                generate_report_wrapper.visualization_template.visualization_diagram_types
            )
            .set_posts_categories(
                [category for category in generate_report_wrapper.model_metadata.category_mapping.values()]
            )
            .set_report_name(generate_report_wrapper.generate_report_metadata.name)
            .set_total_messages_count(handled_data["total_messages"])
            .set_data(handled_data["data"])
            .set_report_warnings(self._report_generation_warnings)
            .build()
        )

    def _save_data_to_file(self, report_id: int, file: TextIO) -> None:
        self._statistics_service.save_report_data(report_id=report_id, data=file, file_type="csv")

    def _reverse_dict_keys(self, dct: dict[str, Any]) -> dict[str, Any]:
        dct_reverted_keys = list(dct.keys())[::-1]

        return {
            key: dct[key] for key in dct_reverted_keys
        }

    def _initialize_report_data_dict(
        self,
        generate_report_wrapper: GenerationTemplateWrapper,
    ) -> dict[str | RawContentTypes, Any]:
        _report_data = {}

        for content_type in generate_report_wrapper.visualization_template.content_types:
            _report_data[content_type] = self._initialize_diagram_type(
                diagram_type=content_type,
                generate_report_meta=generate_report_wrapper.generate_report_metadata,
                model_metadata=generate_report_wrapper.model_metadata
            )

        return {
            "total_messages": 0,
            "data": _report_data,
        }

    def _initialize_diagram_type(
        self,
        diagram_type: RawContentTypes,
        generate_report_meta: GenerateReportEntity,
        model_metadata: ModelEntity,
    ) -> dict[str, Any]:
        if diagram_type == RawContentTypes.BY_CHANNEL:
            return {channel: 0 for channel in generate_report_meta.channel_list}
        if diagram_type == RawContentTypes.BY_CATEGORY:
            return {category: 0 for category in model_metadata.category_mapping.values()}
        if diagram_type == RawContentTypes.BY_CHANNEL_BY_CATEGORY:
            return {
                channel: {
                    category: 0 for category in model_metadata.category_mapping.values()
                }
                for channel in generate_report_meta.channel_list
            }
        if diagram_type == RawContentTypes.BY_DAY_HOUR:
            return {str(hour): 0 for hour in range(24)}

        return {}
