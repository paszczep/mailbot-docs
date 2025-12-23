from logging import info, warning
from concurrent.futures import ThreadPoolExecutor
from app.src.directories import RepoDirs
from app.src.memory import Memory, NoMemory
from app.src.sftp import SftpFiles, SftpError
from app.src.message import Message, ChangedFile, HTML
from app.src.repository import SvnError
from app.src.email import Email


def _data() -> tuple[RepoDirs, SftpFiles]:
    """Zrównoleglenie pobierania danych z SVN i serwera SFTP."""
    with ThreadPoolExecutor(max_workers=2) as pool:
        repo_future = pool.submit(RepoDirs.repository)
        ftp_future = pool.submit(SftpFiles)

        fresh = repo_future.result()
        sftp = ftp_future.result()
    sftp.log()
    fresh.log("current")
    return fresh, sftp


def _memory() -> RepoDirs:
    """Stan repozytorium z momentu ostatniego uruchomienia."""
    memory = Memory.retrieve()
    memory.log("memory")
    return memory


def _difference(fresh: RepoDirs, memory: RepoDirs) -> RepoDirs:
    """Różnica pomiędzy bieżącym a zapamiętanym stanem plików repozytorium."""
    difference = fresh - memory
    difference.log("difference")
    return difference


def _message(difference: RepoDirs, sftps: SftpFiles) -> str:
    """Zbuduj wiadomość. Wstęp informuje o plikach SFTP, jeśli takie występują."""
    content = Message.beginning(
        any_sftps=sftps.any_particular(documents=difference.all_documents)
    )
    for path, files in difference.items():
        content += Message.directory(path=path, files=ChangedFile.create(files, sftps))
    return HTML.pretty(content)


def _execute():
    """Pobierz dane. Sprawdź pamięć, jeśli jest porównaj ją ze stanem teraźniejszym i wyślij raport.
    Zapisz stan teraźniejszy w pamięci."""
    fresh, sftp = _data()
    try:
        memory = _memory()
    except NoMemory:
        info("No memory yet.")
    else:
        if difference := _difference(fresh, memory):
            Email(_message(difference, sftp)).send()
            info("Message sent.")
        else:
            info("No new files!")
    finally:
        Memory.store(fresh)


def run():
    """Wykonaj program, ostrzeż o błędach."""
    try:
        _execute()
    except (SftpError, SvnError) as e:
        warning(e)
