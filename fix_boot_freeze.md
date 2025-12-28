# Naprawa problemu z zawieszaniem się systemu podczas bootowania

## Problem
System Raspberry Pi zawiesza się podczas bootowania na różnych usługach:
- `WayVNCControlService`
- `rpc.statd` lub `rpc-statd-notify.service`
- `cups.service` lub `cups-browsed.service` (drukowanie sieciowe)
- `NetworkManager-dispatcher.service` (skrypty sieciowe)

Te usługi mogą powodować losowe zawieszenia (raz działa, raz się zawiesza). Żadna z nich nie jest potrzebna do działania maski spawalniczej.

## Rozwiązanie

### Opcja 1: Wyłączenie problematycznych usług (zalecane)

Połącz się przez SSH lub użyj klawiatury/monitora w trybie recovery i wykonaj:

```bash
# Wyłącz usługę WayVNC
sudo systemctl disable wayvnc
sudo systemctl stop wayvnc
sudo systemctl mask wayvnc-control.service

# Wyłącz usługi RPC (NFS - nie są potrzebne dla maski)
sudo systemctl disable rpc-statd.service
sudo systemctl disable rpc-statd-notify.service
sudo systemctl mask rpc-statd.service
sudo systemctl mask rpc-statd-notify.service
# Wyłącz CUPS (drukowanie sieciowe - nie jest potrzebne)
sudo systemctl disable cups-browsed.service
sudo systemctl mask cups-browsed.service
# Opcjonalnie: wyłącz cały NFS jeśli nie jest używany
sudo systemctl disable nfs-client.target
sudo systemctl mask nfs-client.target

# Zrestartuj system
sudo reboot
```

### Opcja 2: Usunięcie WayVNC (jeśli nie jest potrzebny)

```bash
# Usuń pakiet WayVNC
sudo apt remove --purge wayvnc

# Wyczyść pozostałości
sudo apt autoremove
sudo apt clean

# Zrestartuj
sudo reboot
```

### Opcja 3: Napraw konfigurację (jeśli WayVNC jest potrzebny)

```bash
# Sprawdź status usługi
sudo systemctl status wayvnc

# Przeedytuj konfigurację jeśli jest błąd
sudo nano /etc/systemd/system/wayvnc.service

# Przeładuj konfigurację systemd
sudo systemctl daemon-reload
sudo systemctl restart wayvnc
```

### Tryb Recovery (jeśli nie można się zalogować)

1. Wyłącz Raspberry Pi
2. Wyjmij kartę SD i włóż do komputera
3. Otwórz partycję boot (`/boot` lub `/boot/firmware`)
4. Edytuj plik `cmdline.txt` i dodaj na końcu linii (bez nowej linii):
   ```
   systemd.unit=rescue.target
   ```
5. Włóż kartę do Raspberry Pi i uruchom
6. System uruchomi się w trybie rescue
7. Wykonaj komendy z Opcji 1
8. Usuń `systemd.unit=rescue.target` z `cmdline.txt`
9. Zrestartuj

## Konfiguracja autostartu programu (po naprawie bootowania)

Utwórz usługę systemd dla programu AR:

```bash
sudo nano /etc/systemd/system/welding-mask.service
```

Zawartość:
```ini
[Unit]
Description=Welding AR Mask Display
After=network.target

[Service]
Type=simple
User=maska
WorkingDirectory=/home/maska
ExecStart=/usr/bin/python3 /home/maska/program.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Aktywuj usługę:
```bash
sudo systemctl daemon-reload
sudo systemctl enable welding-mask.service
sudo systemctl start welding-mask.service

# Sprawdź status
sudo systemctl status welding-mask.service
```

## Weryfikacja

Po restarcie sprawdź logi:
```bash
# Sprawdź logi bootowania
journalctl -b

# Sprawdź status usług
systemctl list-units --failed

# Sprawdź logi programu
journalctl -u welding-mask.service -f
```
