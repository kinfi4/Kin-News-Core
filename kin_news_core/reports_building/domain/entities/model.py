import os

from pydantic import BaseModel, Field

from kin_news_core.reports_building.types import CategoryMapping
from kin_news_core.reports_building.constants import ModelTypes, ModelStatuses


class ModelValidationEntity(BaseModel):
    name: str
    code: str
    owner_username: str = Field(..., alias="ownerUsername")
    model_type: ModelTypes = Field(..., alias="modelType")
    category_mapping: CategoryMapping = Field(..., alias="categoryMapping")

    class Config:
        allow_population_by_field_name = True

    def get_model_directory_path(self, model_storage_path: str) -> str:
        return os.path.join(model_storage_path, self.owner_username, self.code)

    def get_model_binaries_path(self, model_storage_path: str) -> str:
        return os.path.join(model_storage_path, self.owner_username, self.code, "model")

    def get_tokenizer_binaries_path(self, model_storage_path: str) -> str:
        return os.path.join(model_storage_path, self.owner_username, self.code, "tokenizer")


class ModelEntity(ModelValidationEntity):
    model_status: ModelStatuses = Field(..., alias="modelStatus")
    validation_message: str | None = Field(None, alias="validationMessage")


class CustomModelRegistrationEntity(BaseModel):
    name: str
    code: str
    owner_username: str = Field(..., alias="ownerUsername")
    category_mapping: CategoryMapping = Field(..., alias="categoryMapping")

    class Config:
        allow_population_by_field_name = True
