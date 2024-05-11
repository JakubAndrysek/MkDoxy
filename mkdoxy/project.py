from mkdoxy.cache import Cache


class ProjectContext:
    def __init__(self, cache: Cache) -> None:
        self.cache = cache
        self.linkPrefix: str = ""
