from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Iterable
from lxml import etree, html
from app.src.sftp import SftpFiles
from app.src.file import RepoFile


class HTML:

    @staticmethod
    def pretty(html_str: str) -> str:
        tree = html.fromstring(html_str)
        return etree.tostring(tree, pretty_print=True, method="html").decode()

    @staticmethod
    def ul(li_elements: Iterable[str]) -> str:
        return "\n".join(["<ul>", *li_elements, "</ul>"])

    @staticmethod
    def li(element: str) -> str:
        return f"<li>{element}</li>"

    @staticmethod
    def br() -> str:
        return "<br>"

    @staticmethod
    def h3(text: str) -> str:
        return f"<h3>{text}</h3>"

    @staticmethod
    def bold(text: str) -> str:
        return f"<b>{text}</b>"

    @staticmethod
    def italic(text: str) -> str:
        return f"<i>{text}</i>"


@dataclass
class ChangedFile:
    """Plik repozytorium, który uległ zmianie, wraz z ewentualnymi odpowiednikami SFTP."""

    file: PurePosixPath
    sftps: list[PurePosixPath] = field(default_factory=list)

    @classmethod
    def create(cls, files: list[RepoFile], sftp: SftpFiles) -> list["ChangedFile"]:
        """Znajdź odpowiadające pliki SFTP wewnątrz puli wszystkich."""
        return [cls(file.name, sftp.find(file.document)) for file in files]


class Message:
    """Treść wiadomości - zgrupowane pod ścieżkami folderów listy nowych plików repozytorium, 
    wraz z ewentualnymi starszymi ich wersjami na SFTP."""

    _folders: str = "Aktualizowano foldery dokumentacji"
    _svn: str = "Elementy, które uległy zmianie"
    _sftp: str = "oraz ich ewentualne odpowiedniki opublikowane w Intranecie:"

    @staticmethod
    def _single_point(text: str) -> str:
        return HTML.ul([HTML.li(text)])

    @staticmethod
    def beginning(any_sftps: bool = False) -> str:
        """Początek wiadomości, z 'legendą'. Jeśli występują pliki STFP jest to określane."""
        tail = ", " + Message._single_point(Message._sftp) if any_sftps else ":"
        return HTML.h3(Message._folders) + Message._single_point(Message._svn + tail)

    @staticmethod
    def sftp_file(file: PurePosixPath) -> str:
        # point = HTML.bold(file.stem) + HTML.br() + HTML.italic(str(file))
        return HTML.li(str(file.name))

    @staticmethod
    def sftp_files(sftps: list[PurePosixPath]) -> str:
        return HTML.ul(Message.sftp_file(f) for f in sftps)

    @staticmethod
    def repo_file(changed: ChangedFile) -> str:
        """Plik repozytorium i jego ewentualne odpowiedniki SFTP."""
        return HTML.li(
            str(changed.file)
            + (Message.sftp_files(changed.sftps) if changed.sftps else "")
        )

    @staticmethod
    def repo_files(files: list[ChangedFile]) -> str:
        """Zmienione pliki repozytorium z jednego folderu."""
        return HTML.ul(Message.repo_file(f) for f in files)

    @staticmethod
    def directory(path: PurePosixPath, files: list[ChangedFile]) -> str:
        """Ścieżka dostępu do folderu w repozytorium i jego zmienione pliki."""
        return HTML.h3(str(path)) + Message.repo_files(files)
