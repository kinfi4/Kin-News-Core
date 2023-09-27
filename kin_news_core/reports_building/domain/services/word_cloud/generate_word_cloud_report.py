import json
import tempfile
from collections import Counter
from typing import Any

from kin_news_core.datasources.common import DatasourceLink
from kin_news_core.messaging import AbstractEventProducer
from kin_news_core.reports_building.domain.entities import WordCloudReport, GenerationTemplateWrapper
from kin_news_core.reports_building.domain.services.datasources.interface import IDataSourceFactory
from kin_news_core.reports_building.domain.services.generate_report import IGeneratingReportsService
from kin_news_core.reports_building.domain.services.predicting.predictor import IPredictorFactory
from kin_news_core.reports_building.domain.services.word_cloud.reports_builder import (
    WordCloudReportBuilder,
)
from kin_news_core.reports_building.infrastructure.services import StatisticsService, ModelTypesService


class GenerateWordCloudReportService(IGeneratingReportsService):
    _MAX_MOST_COMMON_WORDS = 450
    reports_builder = WordCloudReportBuilder

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

    def _build_report_entity(self, generate_report_wrapper: GenerationTemplateWrapper) -> WordCloudReport:
        gathered_results = self.__gather_data(generate_report_wrapper)

        return (
            WordCloudReportBuilder.from_report_id(generate_report_wrapper.generate_report_metadata.report_id)
            .set_posts_categories([category for category in generate_report_wrapper.model_metadata.category_mapping.values()])
            .set_report_name(generate_report_wrapper.generate_report_metadata.name)
            .set_total_words_count(gathered_results["total_words"])
            .set_data_by_category(gathered_results["data_by_category"])
            .set_data_by_channel(gathered_results["data_by_channel"])
            .set_total_words_frequency(gathered_results["total_words_frequency"])
            .set_data_by_channel_by_category(gathered_results["data_by_channel_by_category"])
            .build()
        )

    def __gather_data(self, generate_report_wrapper: GenerationTemplateWrapper) -> dict[str, Any]:
        datasource = self._datasource_factory.get_data_source(generate_report_wrapper.generate_report_metadata.datasource_type)

        generate_report_meta = generate_report_wrapper.generate_report_metadata
        predictor = generate_report_wrapper.predictor

        _data = self._initialize_data(
            channels=generate_report_meta.channel_list,
            categories=[category for category in generate_report_wrapper.model_metadata.category_mapping.values()],
        )

        for source_name in generate_report_meta.channel_list:
            posts = datasource.fetch_data(source=DatasourceLink(
                source_link=source_name,
                offset_date=self._datetime_from_date(generate_report_meta.end_date, end_of_day=True),
                earliest_date=self._datetime_from_date(generate_report_meta.start_date),
                skip_messages_without_text=True,
            ))

            self._logger.info(f"[GenerateWordCloudReportService] Gathered {len(posts)} messages from {source_name}")

            for message in posts:
                message_text_preprocessed = predictor.preprocess_and_lemmatize(message.text)

                news_category = predictor.predict(message.text)

                message_words = message_text_preprocessed.split()
                words_counted = Counter(message_words)

                _data["total_words"] += len(message_words)

                _data["total_words_frequency"].update(words_counted)

                _data["data_by_channel"][source_name].update(words_counted)

                _data["data_by_category"][news_category].update(words_counted)

                _data["data_by_channel_by_category"][source_name][news_category].update(words_counted)

        self._save_word_cloud_data_to_file(generate_report_meta.report_id, _data)

        return {
            "total_words": _data["total_words"],
            "data_by_channel_by_category": self._truncate_only_most_popular_words(_data["data_by_channel_by_category"]),
            "data_by_category": self._truncate_only_most_popular_words(_data["data_by_category"]),
            "data_by_channel": self._truncate_only_most_popular_words(_data["data_by_channel"]),
            "total_words_frequency": _data["total_words_frequency"].most_common(self._MAX_MOST_COMMON_WORDS),
        }

    def _save_word_cloud_data_to_file(self, report_id: int, _data: dict[str, int]) -> None:
        tmp_file = tempfile.NamedTemporaryFile()

        with open(tmp_file.name, "w") as file:
            encoded_data = json.dumps(_data)
            file.write(encoded_data)

        with open(tmp_file.name, "r") as file:
            self._statistics_service.save_report_data(report_id=report_id, data=file, file_type="json")

    def _truncate_only_most_popular_words(self, data: dict[str, Any]) -> dict[str, Any]:
        result_data: dict[str, Any] = {}

        for key, word_freq in data.items():
            if isinstance(word_freq, Counter):
                result_data[key] = word_freq.most_common(self._MAX_MOST_COMMON_WORDS)
                continue

            result_data[key] = self._truncate_only_most_popular_words(word_freq)

        return result_data

    @staticmethod
    def _initialize_data(channels: list[str], categories: list[str]) -> dict[str, Any]:
        return {
            "total_words": 0,
            "total_words_frequency": Counter(),
            "data_by_channel": {
                channel_name: Counter() for channel_name in channels
            },
            "data_by_category": {
                news_category: Counter() for news_category in categories
            },
            "data_by_channel_by_category": {
                channel_name: {
                    news_category: Counter() for news_category in categories
                } for channel_name in channels
            }
        }
