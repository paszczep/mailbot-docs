from smtplib import SMTP
from ssl import create_default_context
from dataclasses import dataclass, field
from pathlib import Path
from tomllib import load as load_toml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.src.environment import Environment


@dataclass(frozen=True)
class Sender:
    """Wartości kluczowe dla wysyłającej skrzynki email."""

    user: str
    password: str
    port: int
    server: str

    @classmethod
    def values(cls) -> "Sender":
        return cls(**Environment.variables("email"))


def _recipients() -> set[str]:
    """Odbiorcy wiadomości z pliku konfiguracyjnego."""
    with Path("emails.toml").open("rb") as f:
        return set(load_toml(f)["emails"])


@dataclass
class Email:
    """Wysyłana wiadomość email."""

    content: str
    subject: str = 'Oki doki test'
    sender: Sender = Sender.values()
    recipients: set[str] = field(default_factory=_recipients)

    def _msg(self) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["Subject"] = self.subject
        message["From"] = self.sender.user
        message["To"] = ", ".join(self.recipients)
        message.attach(MIMEText(self.content, "html"))
        return message

    def send(self):
        with SMTP(self.sender.server, self.sender.port) as server:
            server.starttls(context=create_default_context())
            server.login(self.sender.user, self.sender.password)
            server.sendmail(self.sender.user, self.recipients, self._msg().as_string())
