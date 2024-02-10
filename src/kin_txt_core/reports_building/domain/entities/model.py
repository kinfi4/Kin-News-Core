import os

from pydantic import ConfigDict, BaseModel, Field

from kin_txt_core.reports_building.domain.entities import PreprocessingConfig
from kin_txt_core.reports_building.types import CategoryMapping
from kin_txt_core.reports_building.constants import ModelTypes, ModelStatuses


class ModelValidationEntity(BaseModel):
    name: str
    code: str
    owner_username: str = Field(..., alias="ownerUsername")
    model_type: ModelTypes = Field(..., alias="modelType")
    category_mapping: CategoryMapping = Field(..., alias="categoryMapping")
    preprocessing_config: PreprocessingConfig = Field(..., alias="preprocessingConfig")

    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())

    def get_model_directory_path(self, model_storage_path: str) -> str:
        return os.path.join(model_storage_path, self.owner_username, self.code)

    def get_model_binaries_path(self, model_storage_path: str) -> str:
        return os.path.join(model_storage_path, self.owner_username, self.code, "model")

    def get_tokenizer_binaries_path(self, model_storage_path: str) -> str:
        return os.path.join(model_storage_path, self.owner_username, self.code, "tokenizer")


class ModelEntity(ModelValidationEntity):
    model_status: ModelStatuses = Field(..., alias="modelStatus")
    validation_message: str | None = Field(None, alias="validationMessage")

    model_config = ConfigDict(protected_namespaces=())

    def get_stop_words_path(self, model_storage_path: str) -> str | None:
        if self.preprocessing_config.remove_stop_words:
            return os.path.join(model_storage_path, self.owner_username, self.code, "stop_words")

        return None


class CustomModelRegistrationEntity(BaseModel):
    name: str
    code: str
    owner_username: str = Field(..., alias="ownerUsername")
    category_mapping: CategoryMapping = Field(..., alias="categoryMapping")
    preprocessing_config: PreprocessingConfig = Field(..., alias="preprocessingConfig")

    model_config = ConfigDict(populate_by_name=True)
