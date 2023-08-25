class PredictorMetaClass(type):
    def __init__(cls, name, bases, clsdict) -> None:
        super().__init__(name, bases, clsdict)

        if getattr(cls, "model_type_code_list", None) is None:
            raise TypeError("Predictor class MUST have model_type_code_list attribute with supported model types")
