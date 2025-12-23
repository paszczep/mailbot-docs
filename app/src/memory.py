from redis import Redis
from pickle import loads, dumps
from app.src.directories import RepoDirs


class NoMemory(Exception):
    """Pamięć jest pusta."""
    pass


class Memory:
    """Pamięć stanu plików w repozytorium."""

    _redis = Redis(host="redis")
    _key: str = "svn_files"

    @classmethod
    def clear(cls):
        """Wyczyść pamięć."""
        cls._redis.delete(cls._key)

    @classmethod
    def store(cls, input: RepoDirs):
        """Zapisz stan."""
        cls._redis.set(cls._key, dumps(input))

    @classmethod
    def retrieve(cls) -> RepoDirs:
        """Pobierz pamięć."""
        memory = cls._redis.get(cls._key)
        if isinstance(memory, bytes):
            return loads(memory)
        raise NoMemory
