from pydantic import BaseModel, Field


class PreprocessingConfig(BaseModel):
    lowercase: bool = Field(default=True)
    remove_links: bool = Field(default=True, alias="removeLinks")
    remove_emoji: bool = Field(default=True, alias="removeEmoji")
    remove_punctuation: bool = Field(default=True, alias="removePunctuation")
    remove_extra_spaces: bool = Field(default=True, alias="removeExtraSpaces")
    remove_html_tags: bool = Field(default=True, alias="removeHtmlTags")

    remove_stop_words: bool = Field(default=True, alias="removeStopWords")
    custom_stop_words: bool = Field(default=False, alias="customStopWords")
