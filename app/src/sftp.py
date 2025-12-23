from paramiko import SSHClient, AutoAddPolicy, SFTPClient, SFTPAttributes
from stat import S_ISDIR
from pathlib import PurePosixPath
from dataclasses import dataclass, field
from typing import ClassVar, Iterator
from contextlib import suppress
from logging import info
from app.src.environment import Environment, safe
from app.src.document import Document, NoSymbol


@dataclass
class _Server:
    """Klucze dostępu SFTP do serwera aplikacji Intranet."""

    host: str
    user: str
    password: str
    root: ClassVar[PurePosixPath] = PurePosixPath("/phocadownload")

    @classmethod
    def env(cls) -> "_Server":
        return cls(**Environment.variables("sftp"))


class SftpError(Exception):
    pass


_sftp_safe = safe(catch=Exception, raise_as=SftpError, message="SFTP server error")


class _Connection:
    """Połączenie z serwerem SFTP."""

    _server: _Server
    _sftp: SFTPClient
    _ssh: SSHClient

    def __init__(self):
        self._server = _Server.env()
        self._ssh = SSHClient()
        self._ssh.set_missing_host_key_policy(AutoAddPolicy())

    @_sftp_safe
    def __enter__(self) -> "_Connection":
        self._ssh.connect(
            hostname=self._server.host,
            username=self._server.user,
            password=self._server.password,
        )
        self._sftp = self._ssh.open_sftp()
        return self

    def __exit__(self, exc, *_):
        try:
            self._sftp.close()
        finally:
            self._ssh.close()

    @_sftp_safe
    def _list(self, path: PurePosixPath) -> list[SFTPAttributes]:
        return self._sftp.listdir_attr(str(path))

    def walk(
        self, path: PurePosixPath = _Server.root
    ) -> Iterator[tuple[PurePosixPath, PurePosixPath]]:
        """Przejkdź po lokalizacjach SFTP, zwracaj ścieżki i nazwy plików PDF."""
        for entry in self._list(path):
            full_path = path / (name := entry.filename)
            if (mode := entry.st_mode) is None:
                continue
            elif S_ISDIR(mode):
                yield from self.walk(full_path)
            else:
                if full_path.suffix.lower() == ".pdf":
                    yield path.relative_to(self._server.root), PurePosixPath(name)


@dataclass
class _File:
    """Plik SFTP. Ścieżka folderu, nazwa pliku z rozszerzeniem i oznaczenie dokumentu."""
    path: PurePosixPath
    name: PurePosixPath
    document: Document = field(init=False)

    def __post_init__(self):
        self.document = Document(self.name)


class SftpFiles(list[_File]):

    def __init__(self):
        """Zaczytaj pliki SFTP, jeśli zawierają oznaczenie dokumentu."""
        super().__init__()
        with _Connection() as connection:
            for path, name in connection.walk():
                with suppress(NoSymbol):
                    self.append(_File(path, name))

    def find(self, document: Document) -> list[PurePosixPath]:
        """Zwraca listę pełnych ścieżek wcześniejszych i aktualnych wersji dokumentu."""
        return [el.path / el.name for el in self if el.document <= document]

    def any_particular(self, documents: set[Document]) -> bool:
        """Czy którykolwiek z podanych dokumentów występuje w tym zbiorze."""
        return any(d.document in documents for d in self)
    
    def log(self):
        info(f"SFTP files: {len(self)}")
