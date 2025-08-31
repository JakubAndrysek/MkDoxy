from typing import Any


class Cache:
    def __init__(self) -> None:
        self.cache: dict[str, Any] = {}

    def add(self, key: str, value: Any) -> None:
        self.cache[key] = value

    def get(self, key: str) -> Any:
        if key in self.cache:
            return self.cache[key]
        else:
            raise KeyError(f"Key: {key} not found in cache!")
