from abc import ABC, abstractmethod

__all__ = ["ITextPreprocessor"]


class ITextPreprocessor(ABC):
    @abstractmethod
    def preprocess_text(self, text: str) -> str:
        pass

    @abstractmethod
    def preprocess_and_lemmatize(self, text: str) -> str:
        pass
