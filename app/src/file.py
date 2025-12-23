from functools import cache
from dataclasses import dataclass, fields, field
from datetime import datetime
from pathlib import PurePosixPath
from app.src.document import Document

@dataclass
class RepoFile:
    """Plik w repozytorium. Wartości, które oferuje API SVN i identyfikacja dokumentu."""
    name: PurePosixPath
    author: str
    commit_revision: int
    date: datetime
    size: int
    document: Document = field(init=False)

    def __post_init__(self):
        self.name = PurePosixPath(self.name)
        self.document = Document(self.name)

    @classmethod
    @cache
    def _fields(cls) -> set[str]:
        """Odczytaj z API pola, których potrzebujesz."""
        return {f.name for f in fields(cls)}

    @classmethod
    def create(cls, element: dict) -> "RepoFile":
        """Utwórz obiekt klasy w oparciu o wykorzystywane wartości z API."""
        clean = {k: v for k, v in element.items() if k in cls._fields()}
        return cls(**clean)

    def __hash__(self) -> int:
        return hash((self.name, self.commit_revision))

    def __eq__(self, other: object) -> bool:
        """Pliki porównywane są przy śledzeniu zmian w repozytorium."""
        if not isinstance(other, RepoFile):
            return NotImplemented
        return self.name == other.name and self.commit_revision == other.commit_revision
