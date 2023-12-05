from fastapi import Request

from dataclasses import dataclass

__all__ = ["InternalUrl"]


@dataclass(frozen=True)
class InternalUrl:
    url: str
    method: str

    def satisfies_request(self, request: Request) -> bool:
        return self.url in request.url.path and self.method == request.method
