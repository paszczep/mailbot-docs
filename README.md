Wyślij raport, jeśli edytowano dokumentację.

# Założenia
Dokumentacja znajduje się na *SVN*. Niektóre dokumenty opublikowane są na platformie WEB. Edycja dokumentu wymaga jego aktualizacji tam, gdzie jest udostępniony. Celem niniejszej aplikacji jest automatyzacja generowania informacji e-mail o konieczności aktualizacji pliku.

# Działanie
- Odczytywany z *SVN* i zapisywany w *Redis* jest stan wersjonowanych dokumentów wewnątrz repozytorium. 
- Przy kolejnym uruchomieniu sprawdzana jest różnica pomiędzy aktualnym, a zapisanym stanem. 
- Poprzez *SFTP* sprawdzana jest obecność starszych wersji nowych dokumentów na serwerze aplikacji  udostępniającej dokumentację.
- Generowana jest wiadomość zawierająca zgrupowane pod ścieżkami swoich folderów listy nowych plików, wraz z ewentualnymi udostępnionymi starszymi ich wersjami.

# Elementy
- Plik `.env`
    - klucze do serwisów zewnętrznych
- Plik `emails.toml`
    - konfiguracja odbiorców raportu
    - edycje odczytywane w czasie rzeczywistym
- `Makefile`
    - uruchamianie aplikacji
- Kontener *Python* 
    - odczyt dokumentacji *SVN*
    - odczyt plików *SFTP*
    - kompilacja i wysyłanie raportu
- Kontener *Redis*
    - Pamięć stanu dokumentacji 

# `.env`
```
email_user=
email_password=
email_port=
email_server=

svn_url=
svn_user=
svn_password=

sftp_host=
sftp_user=
sftp_password=
```

# `emails.toml`
- Plik zawiera listę adresów e-mail, na które przesyłana jest informacja o nowej wersji dokumentu.
- Zmapowany jest jako wolumin wewnątrz kontenera, można zatem edytować adresy e-mail bez konieczności przebudowania kontenera.

# `Makefile`
W CLI w floderze projektu `make` +
- `go` - zbuduj i uruchom kontenery aplikacji
- `logs` - logi działającej aplikacji
- `kill` - zatrzymaj działającą aplikację
- `remove` - usuń obrazy kontenerów aplikacji

# Dostęp *SFTP* do serwera 
Aplikacja wymaga użytkownika z dostępem odczytu miejsca, w którym przechowywana jest dokumentacja, na serwerze aplikacji udostępniającej.
```
sudo adduser (...)

sudo apt-get install -y acl

sudo setfacl -R -m u:czytajdoki:rx (...) # dokumentacja
sudo setfacl -R -d -m u:czytajdoki:rx (...)
```
```
sudo nano /etc/ssh/sshd_config
```
Na **dole** pliku zamień/dodaj:
```
# Zamień istniejący wpis `sftp` na:
Subsystem sftp internal-sftp

# Na końcu pliku dodaj:
Match User czytajdoki
    ChrootDirectory (...) # folder rodzic dokumentacji
    ForceCommand internal-sftp
    X11Forwarding no
    AllowTCPForwarding no
```
```
sudo systemctl restart sshd
```
# mailbot-docs
# mailbot-docs
