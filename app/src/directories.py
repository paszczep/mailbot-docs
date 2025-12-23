from pathlib import PurePosixPath
from collections import defaultdict
from logging import info
from typing import Literal
from app.src.repository import Repository
from app.src.file import RepoFile
from app.src.document import Document


class RepoDirs(defaultdict[PurePosixPath, list[RepoFile]]):
    """Ścieżki dostępu do folderów repozytorium i zawarte w nich dokumenty."""

    def __init__(self, *args, **kwargs):
        """Z argumentami obiekt odtwarzany jest z pamięci. 
        Bez argumentów powstaje w klasowej metodzie tworzącej."""
        if args:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(list)

    @classmethod
    def repository(cls) -> "RepoDirs":
        """Akumulacja wartości z repozytorium plików pod kluczami zawierających je folderów."""
        d = cls()
        for path, file in Repository():
            d[path].append(file)
        return d

    def __sub__(self, other: "RepoDirs") -> "RepoDirs":
        """Różnica pomiędzy obiektami."""
        diff = RepoDirs()
        for path, files in self.items():
            other_files = set(other.get(path, []))
            for f in files:
                if f not in other_files:
                    diff[path].append(f)
        return diff

    def log(self, source: Literal["current", "memory", "difference"]):
        """Logowanie ilości ścieżek i plików w repozytorium, pamięci, lub różnicy między nimi."""
        count = sum(len(_f) for _f in self.values())
        info(f"{source.capitalize()}: {len(self)} paths, {count} files total.")
    
    @property
    def all_documents(self) -> set[Document]:
        """Wszystkie dokumenty, żeby sprawdzić czy jakieś są na SFTP."""
        return {file.document for files in self.values() for file in files}
