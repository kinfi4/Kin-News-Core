from abc import ABCMeta, ABC

from kin_txt_core.reports_building.domain.entities import CustomModelRegistrationEntity


class PredictorValidateModelType(ABCMeta):
    def __init__(cls, name, bases, clsdict) -> None:
        super().__init__(name, bases, clsdict)

        # TODO: Find out the case when mro()[1], how does it happen?
        if cls.mro()[1] is ABC or cls.mro()[0] is ABC:  # That means that user is defining an abstract class, and we don't need to validate it
            return

        model_types = getattr(cls, "model_types", None)

        if model_types is None:
            raise TypeError("Predictor class MUST have model_type_code_list attribute with supported model types")

        if isinstance(model_types, str) and model_types == "GenericModel":
            return

        for model_type in model_types:
            if not isinstance(model_type, CustomModelRegistrationEntity):
                raise TypeError("Predictor class model_types attribute MUST be a list of CustomModelRegistrationEntity or str with GENERIC_MODEL_TYPE value")
