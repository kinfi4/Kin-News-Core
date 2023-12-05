from abc import ABCMeta, ABC

from kin_txt_core.reports_building.domain.entities import CustomModelRegistrationEntity
from kin_txt_core.reports_building.constants import GENERIC_MODEL_TYPE


class PredictorValidateModelType(ABCMeta):
    def __init__(cls, name, bases, clsdict) -> None:
        super().__init__(name, bases, clsdict)

        # TODO: Find out the case when mro()[1], how does it happen?
        if cls.mro()[1] is ABC or cls.mro()[0] is ABC:  # That means that user is defining an abstract class, and we don't need to validate it
            return

        if (model_type := getattr(cls, "model_type", None)) is None:
            raise TypeError("Predictor class MUST have model_type_code_list attribute with supported model types")

        if isinstance(model_type, CustomModelRegistrationEntity):
            return

        if isinstance(model_type, str) and model_type == GENERIC_MODEL_TYPE:
            return

        raise TypeError("Predictor class model_type_code_list attribute MUST be CustomModelRegistrationEntity or str with GENERIC_MODEL_TYPE value")
