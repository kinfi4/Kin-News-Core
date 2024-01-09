from enum import Enum

from pydantic import BaseModel, Field

from kin_txt_core.reports_building.constants import SupportedLanguages


class PossiblePaddingTruncating(str, Enum):
    PRE = "pre"
    POST = "post"


class PreprocessingConfig(BaseModel):
    lowercase: bool = Field(default=True)
    remove_links: bool = Field(default=True, alias="removeLinks")
    remove_emoji: bool = Field(default=False, alias="removeEmoji")
    remove_punctuation: bool = Field(default=True, alias="removePunctuation")
    remove_extra_spaces: bool = Field(default=True, alias="removeExtraSpaces")
    remove_html_tags: bool = Field(default=True, alias="removeHtmlTags")

    remove_stop_words: bool = Field(default=False, alias="removeStopWords")
    stop_words_file_original_name: str | None = Field(default=None, alias="stopWordsFileOriginalName")

    lemmatize_text: bool = Field(default=False, alias="lemmatizeText")
    language: SupportedLanguages | None = Field(default=None, alias="language")

    max_tokens: int | None = Field(default=None, alias="maxTokens")
    padding: PossiblePaddingTruncating = Field(default=PossiblePaddingTruncating.PRE, alias="padding")
    truncating: PossiblePaddingTruncating = Field(default=PossiblePaddingTruncating.PRE, alias="truncating")

    class Config:
        allow_population_by_field_name = True
