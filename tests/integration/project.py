"""Configuration and artifact paths for completed integration builds."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol


@dataclass(frozen=True)
class BuildOptions:
    api_path: str | None = None
    save_api: str | None = None
    use_directory_urls: bool | None = None


@dataclass(frozen=True)
class BuiltProject:
    root: Path
    api_path: str = "api"
    save_api: str = "generated"

    @property
    def generated_dir(self) -> Path:
        cache = self.root / self.save_api if self.save_api else self.root / "site" / "assets" / ".doxy"
        return cache / "api"

    def markdown(self, page: str) -> str:
        return (self.generated_dir / self.api_path / page).read_text(encoding="utf-8")

    def html(self, page: str) -> str:
        return (self.root / "site" / page).read_text(encoding="utf-8")

    @property
    def xml_dir(self) -> Path:
        return self.generated_dir / "xml"


class ProjectBuilder(Protocol):
    def __call__(
        self,
        name: str,
        *,
        options: BuildOptions | None = None,
        prepare: Callable[[Path], None] | None = None,
    ) -> BuiltProject:
        ...
