from typing import Any

from kin_txt_core.datasources.common.entities import ClassificationEntity
from kin_txt_core.reports_building.domain.entities.generation_template_wrapper import GenerationTemplateWrapper
from kin_txt_core.reports_building.domain.services.word_cloud.wc_strategy import WordCloudStrategy


class BuildWordCloudTokenClassificationStrategy(WordCloudStrategy):
    def handle_posts(
        self,
        posts: list[ClassificationEntity],
        generate_report_wrapper: GenerationTemplateWrapper,
    ) -> dict[str, Any]:
        generate_report_meta = generate_report_wrapper.generate_report_metadata
        predictor = generate_report_wrapper.predictor

        _data = self._initialize_data(
            channels=generate_report_meta.channel_list,
            categories=[category for category in generate_report_wrapper.model_metadata.category_mapping.values()],
        )

        for message in posts:
            source_name = message.source_name

            words_to_category_mapping: dict[str, list[str]] = predictor.predict_post_tokens(message)

            for category, word_list in words_to_category_mapping.items():
                if not category:  # usually if category is not recognized it's empty
                    continue

                _data["total_words"] += 1  # for each token was recognized

                _data["total_words_frequency"].update(word_list)

                _data["data_by_channel"][source_name].update(word_list)

                _data["data_by_category"][category].update(word_list)
                _data["data_by_channel_by_category"][source_name][category].update(word_list)

        self._save_word_cloud_data_to_file(generate_report_meta.report_id, _data)

        return {
            "total_words": _data["total_words"],
            "data_by_channel_by_category": self._truncate_only_most_popular_words(_data["data_by_channel_by_category"]),
            "data_by_category": self._truncate_only_most_popular_words(_data["data_by_category"]),
            "data_by_channel": self._truncate_only_most_popular_words(_data["data_by_channel"]),
            "total_words_frequency": _data["total_words_frequency"].most_common(self._MAX_MOST_COMMON_WORDS),
        }
