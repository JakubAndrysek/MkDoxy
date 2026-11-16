"""Paths to the artifacts of a completed integration build."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BuiltProject:
    root: Path

    def markdown(self, page: str) -> str:
        return (self.root / "generated" / "api" / "api" / page).read_text(encoding="utf-8")

    def html(self, page: str) -> str:
        return (self.root / "site" / page).read_text(encoding="utf-8")

    @property
    def xml_dir(self) -> Path:
        return self.root / "generated" / "api" / "xml"
