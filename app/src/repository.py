from svn.remote import RemoteClient
from svn.exception import SvnException
from dataclasses import dataclass
from typing import Iterator, Iterable
from pathlib import PurePosixPath
from contextlib import suppress
from app.src.environment import Environment, safe
from app.src.file import RepoFile
from app.src.document import NoSymbol


@dataclass(frozen=True)
class _Remote:
    """Repozytorium plików dokumentacji produktu."""

    url: str
    user: str
    password: str

    @classmethod
    def _env(cls) -> "_Remote":
        """Odpowiednie wartości ze zmiennych środowiskowych."""
        return cls(**Environment.variables("svn"))

    def _remote(self) -> RemoteClient:
        """Klient zdalnego repozytorium."""
        return RemoteClient(self.url, username=self.user, password=self.password)

    @classmethod
    def client(cls) -> RemoteClient:
        """Utwórz klienta zdalnego repozytorium."""
        return cls._env()._remote()


class SvnError(Exception):
    pass


_repo_safe = safe(
    catch=SvnException, raise_as=SvnError, message="SVN repository error"
)


class Repository(Iterable[tuple[PurePosixPath, RepoFile]]):
    """Nie-archiwalne pliki PDF zawierające dokumentację znajdujące się na repozytorium."""

    remote: RemoteClient

    def __init__(self):
        super().__init__()
        self.remote = _Remote.client()

    @_repo_safe
    def _directory_elements(self) -> Iterator[tuple[str, dict]]:
        """Wymień elementy wewnątrz źródła."""
        return self.remote.list_recursive()

    @staticmethod
    def is_not_archive(path: PurePosixPath) -> bool:
        """Ścieżka dostępu do zasobu nie sugeruje jego archiwalności."""
        return not any(b in str(path).lower() for b in ("/old", "archiwum"))

    @staticmethod
    def is_pdf(file: PurePosixPath) -> bool:
        return file.suffix.lower() == ".pdf"

    def __iter__(self) -> Iterator[tuple[PurePosixPath, RepoFile]]:
        """Przejdź przez wszystkie lokalizacje w repozytorium. 
        Zwracaj nie-archiwalne pliki PDF, jeśli zawierają oznaczenie dokumentu."""
        for _dir, _attrs in self._directory_elements():
            with suppress(NoSymbol):
                repo = RepoFile.create(_attrs)
                path = PurePosixPath(_dir)
                if self.is_pdf(repo.name) and self.is_not_archive(path):
                    yield path, repo
