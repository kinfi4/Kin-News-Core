import json
import os

from fastapi import UploadFile, Form, File
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


class CreateModelEntity(BaseModel):
    name: str
    code: str
    model_type: ModelTypes = Field(..., alias="modelType")
    model_data: UploadFile = Field(..., alias="modelData")
    tokenizer_data: UploadFile = Field(..., alias="tokenizerData")
    category_mapping: CategoryMapping = Field(..., alias="categoryMapping")

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        code: str = Form(...),
        model_type: ModelTypes = Form(..., alias="modelType"),
        category_mapping_string: str = Form(..., alias="categoryMapping"),
        model_data: UploadFile = File(..., alias="modelData"),
        tokenizer_data: UploadFile = File(..., alias="tokenizerData"),
    ) -> "CreateModelEntity":
        loaded_category_mapping = json.loads(category_mapping_string)

        return cls(
            name=name,
            code=code,
            model_type=model_type,
            category_mapping=loaded_category_mapping,
            model_data=model_data,
            tokenizer_data=tokenizer_data
        )

    def save_model_binaries(self, model_storage_path: str, username: str) -> None:
        user_models_path = os.path.join(model_storage_path, username, self.code)

        if not os.path.exists(user_models_path):
            os.makedirs(user_models_path)

        if self.model_data is not None:
            with open(os.path.join(user_models_path, "model"), "wb") as file:
                file.write(self.model_data.file.read())

        if self.tokenizer_data is not None:
            with open(os.path.join(user_models_path, "tokenizer"), "wb") as file:
                file.write(self.tokenizer_data.file.read())


class UpdateModelEntity(CreateModelEntity):
    models_has_changed: bool = Field(False, alias="modelsHasChanged")
    model_data: UploadFile | None = Field(None, alias="modelData")
    tokenizer_data: UploadFile | None = Field(None, alias="tokenizerData")

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        model_type: ModelTypes = Form(..., alias="modelType"),
        category_mapping_string: str = Form(..., alias="categoryMapping"),
        model_data: UploadFile | None = File(None, alias="modelData"),
        tokenizer_data: UploadFile | None = File(None, alias="tokenizerData"),
        models_has_changed: bool = Form(False, alias="modelsHasChanged"),
    ) -> "UpdateModelEntity":
        loaded_category_mapping = json.loads(category_mapping_string)

        return cls(
            name=name,
            model_type=model_type,
            category_mapping=loaded_category_mapping,
            model_data=model_data,
            tokenizer_data=tokenizer_data,
            models_has_changed=models_has_changed
        )