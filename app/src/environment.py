from os import environ
from typing import Literal
from functools import wraps


class Environment:
    @staticmethod
    def variables(scope: Literal["email", "svn", "sftp"]) -> dict:
        """Zmienne środowiskowe z określonym przedroskiem."""
        return {
            key.split("_")[1]: value
            for key, value in environ.items()
            if key.startswith(scope)
        }

def safe(
    *,
    raise_as: type[Exception],
    catch: type[Exception],
    message: str,
):
    """Szkieletowy dekorator do łapania i propagowania błędów."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except catch as e:
                msg = f"{message}: {e}"
                raise raise_as(msg) from e

        return wrapper

    return decorator
