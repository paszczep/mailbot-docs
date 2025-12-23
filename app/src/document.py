from dataclasses import dataclass
from pathlib import PurePosixPath
from re import search, sub, IGNORECASE


class NoSymbol(Exception):
    """Ignorowane są pliki, które nie posidają oznaczenia dokuimentu."""
    pass


@dataclass
class Document:
    """Identyfikacja dokumentu."""

    title: str
    id: tuple[int, int]
    version: tuple[int, int]

    @staticmethod
    def _symbol(filename: str) -> str:
        """Zwraca oznaczenie dokumentu a.b.c.d; gdzie a, b, c, d to liczby."""
        if symbol := search(r"(?<!\d)(\d+\.\d+\.\d+\.\d+)", filename):
            return symbol.group(1)
        else:
            raise NoSymbol

    @staticmethod
    def _normalize_title(stem: str, symbol: str) -> str:
        """Normalizacja tytułu dokumentu na potrzeby różnic w nazwach plików.
        - usuwa 'nr 4.11.1.3', 'v4.11.1.3', 'v 4.11.1.3', albo samo '4.11.1.3'
        - zmienia interpunkcję na spacje
        - usuwa elementy numeryczne
        """
        tmp = sub(rf"\b(?:nr\s+|v\s*)?{symbol}\b", " ", stem, flags=IGNORECASE)
        tmp = sub(r"[^\w]+", " ", tmp)
        parts = [p.lower() for p in tmp.split() if not p.isdigit()]
        return " ".join(parts)

    def __init__(self, file: PurePosixPath):
        symbol = self._symbol(stem := file.stem)
        id_1, id_2, ver_1, ver_2 = [int(v) for v in symbol.split(".")]
        self.id = (id_1, id_2)
        self.version = (ver_1, ver_2)
        self.title = self._normalize_title(stem, symbol)
        # self.title = stem.split()[0]

    def _same_document(self, other: "Document") -> bool:
        """Dopuszcza różne wersje tego samego dokumentu."""
        return self.title == other.title and self.id == other.id

    def __eq__(self, other: object) -> bool:
        """Dokładnie ten sam dokument."""
        if not isinstance(other, Document):
            return NotImplemented
        return self._same_document(other) and self.version == other.version

    def _is_next(self, other: "Document") -> bool:
        """Następna wersja dokumentu - sprawdzenie jedynie numerycznego oznaczenia.
        Prawdziwe np. '1.1.12.1' albo '1.1.11.29' dla '1.1.11.28'."""
        (A, a_min), (B, b_min) = self.version, other.version
        return self.id == other.id and (
            (A == B and b_min == a_min + 1) or (B == A + 1 and b_min == 1)
        )

    def __le__(self, other: "Document") -> bool:
        """Czy porównywany element jest starszą wersją tego samego dokumentu."""
        return (
            self._same_document(other) and self.version <= other.version
        ) or self._is_next(other)

    def __hash__(self) -> int:
        return hash((self.title, self.id, self.version))
