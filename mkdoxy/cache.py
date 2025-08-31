class Cache:
    def __init__(self) -> None:
        self.cache = {}

    def add(self, key: str, value: str) -> None:
        self.cache[key] = value

    def get(self, key: str) -> str:
        if key in self.cache:
            return self.cache[key]
        else:
            raise KeyError(f"Key: {key} not found in cache!")
