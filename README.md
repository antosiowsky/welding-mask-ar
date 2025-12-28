# ENG BELOW! 

# Maska do spawania AR / Welding AR System Using Raspberry Pi Zero 2 W / [PL/ENG]

![mask](https://github.com/user-attachments/assets/1f18e6d2-8269-4ee1-a8ba-2ffd11a6789c)

## Temat Projektu
Projekt dotyczy stworzenia systemu AR wykorzystującego Raspberry Pi Zero 2 W, kamerę oraz wyświetlacz 5,5 cala (1920x1080). System wyświetla na żywo obraz z kamery podzielony na dwie równe połowy, co umożliwia używanie wyświetlacza jako gogli AR.

### Nowe Funkcje (Grudzień 2025)
- **Nagrywanie wideo** - aktywowane przez zakrycie fotorezystora na 5 sekund
- **Adaptacyjne przyciemnianie** - ulepszone algorytmy dla lepszej widoczności w naturalnym świetle
- **Monitoring czujników** - wyświetlanie stanu baterii i jakości powietrza (MQ-07)
- **Wskaźnik nagrywania** - migająca ikona REC podczas nagrywania

## Opis Funkcji Urządzenia
- Pobieranie obrazu z kamery w czasie rzeczywistym (18 FPS, niska latencja).
- Przetwarzanie obrazu w celu poprawienia jakości z adaptacyjną kontrolą ekspozycji.
- Wyświetlanie obrazu na ekranie podzielonym na dwie części (dual-view VR).
- Odczyt danych z czujnika jakości powietrza (MQ-07 CO sensor).
- Odczyt poziomu oświetlenia i automatyczne dostosowanie ekspozycji kamery.
- **Nagrywanie wideo** - nagrywanie tego co widzi operator w formacie MP4.
  - Start/stop: zakryj fotorezystor na 5 sekund
  - Zapis do: `/home/maska/recordings/`
  - Format: MP4 (15 FPS) z pełnym obrazem operatora
- **HUD (Head-Up Display)** z informacjami:
  - Status baterii 18650 (napięcie i poziom)
  - Jakość powietrza (czujnik CO)
  - Czerwona ramka ostrzegawcza przy niebezpiecznym poziomie CO
  - Migająca ikona REC podczas nagrywania

## Uzasadnienie Wyboru Elementów Elektronicznych
- **Raspberry Pi Zero 2 W** - kompaktowa platforma zdolna do obsługi kamer i wyświetlaczy.
- **Kamera Raspberry PI Global Shutter Camera** - kompatybilna z Raspberry Pi, zapewnia niskie opóźnienia.
- **Wyświetlacz 5,5 cala 1920x1080** - pozwala na realistyczne wrażenia AR.
- **MCP3008 (ADC)** - pozwala na odczyt danych z analogowych czujników.
- **Czujnik MQ-07** - detekcja tlenku węgla (CO) w strefie oddechowej operatora.
- **Panel fotowoltaiczny** - odzyskiwanie energii świetlnej łuku spawalniczego (Energy Harvesting).
- **Bateria 2x 18650 Li-Ion** - autonomiczne zasilanie urządzenia.

## Użyte Narzędzia
- **Python 3** - język programowania do obsługi kamery i czujników.
- **OpenCV** - biblioteka do przetwarzania obrazu i nagrywania wideo.
- **Picamera2** - interfejs do kamery Raspberry Pi z kontrolą ekspozycji.
- **Spidev** - obsługa magistrali SPI dla czujnika MCP3008.
- **NumPy** - przetwarzanie macierzy obrazów.

## Budowa Prototypu - Montaż i Rozmieszczenie Komponentów

### Finalny etap prac warsztatowych
Montaż elektroniki oraz optyki wewnątrz przygotowanej obudowy został zaprojektowany tak, aby zapewnić równomierne wyważenie maski oraz optymalne warunki pracy dla sensorów.

#### Panel Frontowy - Sensory i Układy Optyczne

![frontENG](https://github.com/user-attachments/assets/d9cabbe8-28d2-48ae-8142-f79a362ba1cb)

**A – Zespół optyczny kamery**
- Moduł Raspberry Pi Global Shutter Camera
- Filtr UV (ochrona matrycy)
- Filtr szary o regulowanej gęstości ND 2-1000
- Fizyczne ograniczenie światła zwiększające dynamikę układu w warunkach spawania

**B – Panel fotowoltaiczny**
- Ogniwo krzemowe zintegrowane z górną częścią obudowy
- Energy Harvesting - odzyskiwanie energii świetlnej łuku spawalniczego

**C – Fotorezystor**
- Sensor natężenia światła
- Wyzwalacz (trigger) algorytmu adaptacyjnej ekspozycji
- Trigger funkcji nagrywania wideo (zakrycie >5 sekund)

**D – Sensor gazu MQ-07**
- Wlot powietrza do komory pomiarowej czujnika tlenku węgla (CO)
- Umieszczony w strefie oddechowej operatora

#### Wnętrze i Elektronika

![insideENG](https://github.com/user-attachments/assets/297ee58b-2856-4a2e-a16c-637f7b8ffd8b)

**E – Jednostka centralna**
- Mikrokomputer Raspberry Pi Zero 2 W
- Odpowiedzialny za akwizycję i przetwarzanie obrazu w czasie rzeczywistym

**F – Autorska płyta główna (PCB)**
- Obwód drukowany wykonany metodą ablacji laserowej
- Integruje przetwornik ADC (MCP3008) oraz interfejsy czujników
- Zapewnia komunikację SPI między sensorami a jednostką centralną

**G – Moduł zasilania**
- Układ stabilizacji napięcia i ładowania (BMS)
- Zarządzanie dystrybucją energii z baterii i panelu solarnego
- Ochrona przed przeładowaniem i głębokim rozładowaniem

**H – Magazyn energii**
- Pakiet dwóch ogniw Li-Ion typu 18650
- Zapewnia autonomię pracy urządzenia
- Monitorowanie napięcia przez ADC (kanał CH0)

**I – Zespół soczewek VR**
- Fizyczna realizacja projektu uchwytu z soczewkami dwuwypukłymi
- Umożliwia ostre widzenie ekranu z bliskiej odległości (akomodacja oka)
- Regulowana odległość dla dostosowania do użytkownika

**J – Wyświetlacz**
- Panel LCD 5.5 cala o rozdzielczości Full HD (1920x1080)
- Wyświetla obraz stereoskopowy (dual-view) oraz interfejs HUD
- Osadzony w dedykowanej ramce ochronnej

![topENG](https://github.com/user-attachments/assets/54dfbcf4-2357-4185-9818-b52c578b4063)

## Algorytm Oprogramowania

### Inicjalizacja systemu
- Ustawienie rozdzielczości framebuffera (1920x1080).
- Inicjalizacja interfejsu SPI do komunikacji z przetwornikiem ADC MCP3008.
- Konfiguracja kamery Picamera2 z optymalnymi ustawieniami.
- Uruchomienie wątku odpowiedzialnego za przechwytywanie klatek w czasie rzeczywistym.
- Inicjalizacja menedżera nagrywania wideo.

### Pętla główna programu
- Pobranie aktualnej klatki obrazu z kamery (wielowątkowa akwizycja).
- Odczyt wartości z czujników podłączonych do MCP3008:
  - Bateria 18650 (CH0) - dzielnik napięcia 10k/20k
  - Czujnik CO MQ-07 (CH1) - dzielnik 2.2k/3.3k
  - Fotorezystor (CH2) - detekcja światła i trigger nagrywania
- Adaptacyjna kontrola ekspozycji kamery (PID-like smooth controller).
- Detekcja triggera nagrywania (fotorezystor zakryty >5 sekund).
- Przetwarzanie obrazu w celu wygenerowania podwójnego widoku VR.
- Zapis klatki do nagrania wideo (jeśli aktywne).
- Wyświetlenie obrazu na framebufferze wraz z HUD.
- Kontrola częstotliwości odświeżania (18 FPS target).

### Zakończenie programu
- Zatrzymanie nagrywania (jeśli aktywne) i zapis pliku.
- Zatrzymanie wątku przechwytywania klatek.
- Zatrzymanie kamery.
- Zamknięcie połączenia SPI.
- Zamknięcie framebuffera.

## Opis interakcji oprogramowania z układem elektronicznym

### Kamera Picamera2
- Kamera przechwytuje obraz w formacie RGB888 i przekazuje go do programu.
- Obraz jest przetwarzany i wyświetlany na framebufferze.
- Program steruje ustawieniami kamery (jasność, kontrast, czas naświetlania, gain).
- Adaptacyjna kontrola ekspozycji reaguje na warunki oświetleniowe.

### Przetwornik ADC MCP3008 (SPI)
- Czujniki są podłączone do MCP3008, który przekształca ich sygnał analogowy na cyfrowy.
- Program odczytuje wartości z kanałów MCP3008 przez interfejs SPI.
- Dane z czujników są wykorzystywane do:
  - Monitorowania stanu baterii
  - Detekcji niebezpiecznych poziomów CO
  - Adaptacyjnej kontroli ekspozycji kamery
  - Wyzwalania nagrywania wideo

### Framebuffer /dev/fb0
- Obraz przetworzony w programie jest konwertowany do formatu RGB565.
- Wynikowy obraz jest zapisywany bezpośrednio do pliku /dev/fb0, który steruje wyświetlaczem.
- HUD (informacje o czujnikach) jest nakładany na obraz przed zapisem.

## Wnioski z Uruchamiania i Testowania

### Wpływ wydajności sprzętu na jakość obrazu
Raspberry Pi Zero 2 W, mimo swojej kompaktowości, ma ograniczone zasoby obliczeniowe. Wydajność została zoptymalizowana poprzez zmniejszenie rozdzielczości obrazu wejściowego (320x360 per oko) oraz zastosowanie przetwarzania wielowątkowego. Stabilne 18 FPS zapewnia płynny obraz przy niskiej latencji.

Potencjalnym usprawnieniem byłoby użycie Raspberry Pi 4 lub innego mocniejszego układu, co pozwoliłoby na wyższą rozdzielczość i bardziej zaawansowane przetwarzanie obrazu.

### Problemy z kolorami i ich rozwiązanie
Początkowe problemy z odwzorowaniem kolorów wynikały z błędnej konwersji RGB888 do RGB565. Użycie właściwych metod OpenCV (cv2.COLOR_BGR2BGR565) pozwoliło na poprawienie jakości obrazu. Nadal występują drobne przekłamania w bardzo ciemnych obszarach, co można poprawić poprzez lepsze zarządzanie kontrastem.

### Optymalizacja FPS
Początkowo liczba klatek na sekundę była niska (około 10–15 FPS), co powodowało efekt „lag" przy ruchu kamery. Zastosowanie dedykowanego wątku do akwizycji obrazu, optymalizacja wyświetlania framebuffera oraz redukcja częstotliwości odczytu czujników pozwoliły na uzyskanie stabilnych 18 FPS z niską latencją.

Możliwości dalszej poprawy: wykorzystanie sprzętowego kodowania obrazu (h264_v4l2m2m) zamiast programowego przetwarzania przez OpenCV.

## Instalacja i Konfiguracja

### Wymagania
```bash
sudo apt update
sudo apt install python3-opencv python3-picamera2 python3-spidev python3-numpy
```

### Transfer pliku na urządzenie
```bash
scp -i "klucz" -o StrictHostKeyChecking=no program.py maska@192.168.1.105:~/program.py
```

### Autostart przy bootowaniu
Utwórz usługę systemd:
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

[Install]
WantedBy=multi-user.target
```

Aktywacja:
```bash
sudo systemctl daemon-reload
sudo systemctl enable welding-mask.service
sudo systemctl start welding-mask.service
```

### Rozwiązywanie problemów z bootowaniem
Jeśli system zawiesza się podczas bootowania (np. na `WayVNCControlService`, `rpc-statd-notify.service`, `cups.service`, `cups-browsed.service`, `NetworkManager-dispatcher.service`), zobacz [fix_boot_freeze.md](fix_boot_freeze.md) dla szczegółowych instrukcji.

**Szybka naprawa (przez SSH):**
```bash
# Wyłącz wszystkie niepotrzebne usługi powodujące zawieszenia
sudo systemctl disable wayvnc
sudo systemctl mask wayvnc-control.service
sudo systemctl disable rpc-statd.service
sudo systemctl mask rpc-statd-notify.service
sudo systemctl disable cups.service
sudo systemctl disable cups-browsed.service
sudo systemctl mask cups.service
sudo systemctl mask cups-browsed.service
sudo systemctl disable NetworkManager-dispatcher.service
sudo systemctl mask NetworkManager-dispatcher.service

sudo reboot
```

## Potencjalne przyszłe ulepszenia
- ✅ ~~Możliwość nagrywania wideo~~ (zaimplementowane XII 2025)
- Zastosowanie mocniejszego sprzętu (np. Raspberry Pi 4) w celu poprawy wydajności.
- Dodanie filtrów obrazu do lepszego dostosowania jakości wyświetlania.
- Rozszerzenie funkcjonalności AR poprzez śledzenie ruchu głowy lub interakcję z otoczeniem.
- Transmisja obrazu na żywo do innego urządzenia (streaming).
- Dodanie elementu mechanicznego obracającego pokrętłem przysłony obiektywu.
- Zakup lepszego obiektywu.

## Schematy i Dokumentacja Techniczna

![schemat_blokowy](https://github.com/user-attachments/assets/596fdb22-4aad-4948-9483-1b2a79ff850a)

![schema](https://github.com/user-attachments/assets/df591576-924b-4fb6-b2c4-a62a69f624a2)

---

# ENG

# Welding AR System Using Raspberry Pi Zero 2 W

## Project Overview
This project involves creating an Augmented Reality (AR) system using a Raspberry Pi Zero 2 W, a camera, and a 5.5-inch display (1920x1080). The system captures real-time video from the camera and splits it into two equal halves, enabling the display to function as AR goggles.

### New Features (December 2025)
- **Video recording** - activated by covering photoresistor for 5 seconds
- **Adaptive dimming** - improved algorithms for better visibility in natural light
- **Sensor monitoring** - display of battery status and air quality (MQ-07)
- **Recording indicator** - blinking REC icon during recording

## Features
- Real-time video capture from the camera (18 FPS, low latency).
- Image processing for quality enhancement with adaptive exposure control.
- Splitting the video into two sections for VR-like visualization.
- Air quality sensor data reading (MQ-07 CO sensor).
- Light intensity measurement and automatic camera exposure adjustment.
- **Video recording** - records operator's view in MP4 format:
  - Start/stop: cover photoresistor for 5 seconds
  - Saves to: `/home/maska/recordings/`
  - Format: MP4 (15 FPS) with full operator view
- **HUD (Head-Up Display)** showing:
  - 18650 battery status (voltage and level)
  - Air quality (CO sensor)
  - Red warning border for dangerous CO levels
  - Blinking REC icon during recording

## Hardware Components
- **Raspberry Pi Zero 2 W** – A compact platform capable of handling cameras and displays.
- **Raspberry Pi Global Shutter Camera** – Provides low latency and is compatible with Raspberry Pi.
- **5.5-inch 1920x1080 Display** – Offers a high-resolution AR experience.
- **MCP3008 (ADC Converter)** – Reads data from analog sensors.
- **MQ-07 Sensor** - Carbon monoxide (CO) detection in operator's breathing zone.
- **Photovoltaic panel** - Energy harvesting from welding arc light.
- **2x 18650 Li-Ion battery** - Autonomous device power supply.

## Software & Tools
- **Python 3** – Main programming language for device and sensor management.
- **OpenCV** – Library for image processing and video recording.
- **Picamera2** – Raspberry Pi camera interface with exposure control.
- **Spidev** – SPI interface library for MCP3008 communication.
- **NumPy** - Image matrix processing.

## Prototype Construction - Assembly and Component Placement

### Final Workshop Stage
The assembly of electronics and optics inside the prepared housing was designed to ensure even weight distribution of the mask and optimal working conditions for the sensors.

#### Front Panel - Sensors and Optical Systems

![frontENG](https://github.com/user-attachments/assets/d9cabbe8-28d2-48ae-8142-f79a362ba1cb)

**A – Camera Optical Assembly**
- Raspberry Pi Global Shutter Camera module
- UV filter (sensor protection)
- Variable density gray filter ND 2-1000
- Physical light limitation increasing system dynamics in welding conditions

**B – Photovoltaic Panel**
- Silicon cell integrated with the upper part of the housing
- Energy Harvesting - recovery of light energy from welding arc

**C – Photoresistor**
- Light intensity sensor
- Trigger for adaptive exposure algorithm
- Video recording function trigger (>5 seconds coverage)

**D – MQ-07 Gas Sensor**
- Air inlet to carbon monoxide (CO) sensor measurement chamber
- Placed in operator's breathing zone

#### Interior and Electronics

![insideENG](https://github.com/user-attachments/assets/297ee58b-2856-4a2e-a16c-637f7b8ffd8b)

**E – Central Unit**
- Raspberry Pi Zero 2 W microcomputer
- Responsible for real-time image acquisition and processing

**F – Custom Main Board (PCB)**
- Printed circuit board made by laser ablation method
- Integrates ADC converter (MCP3008) and sensor interfaces
- Provides SPI communication between sensors and central unit

**G – Power Module**
- Voltage stabilization and charging circuit (BMS)
- Energy distribution management from battery and solar panel
- Protection against overcharging and deep discharge

**H – Energy Storage**
- Package of two Li-Ion cells type 18650
- Provides device operation autonomy
- Voltage monitoring via ADC (channel CH0)

**I – VR Lens Assembly**
- Physical implementation of holder design with biconvex lenses
- Enables sharp screen viewing from close distance (eye accommodation)
- Adjustable distance for user customization

**J – Display**
- 5.5-inch LCD panel with Full HD resolution (1920x1080)
- Displays stereoscopic image (dual-view) and HUD interface
- Mounted in dedicated protective frame

![topENG](https://github.com/user-attachments/assets/54dfbcf4-2357-4185-9818-b52c578b4063)

### Software Algorithm
#### System Initialization
1. Set framebuffer resolution (1920x1080).
2. Initialize SPI interface for ADC MCP3008 communication.
3. Configure the Picamera2 camera with optimal settings.
4. Start a thread for real-time frame capture.
5. Initialize video recording manager.

#### Main Program Loop
1. Capture the latest frame from the camera (multi-threaded acquisition).
2. Read sensor data from MCP3008:
   - 18650 battery (CH0) - voltage divider 10k/20k
   - MQ-07 CO sensor (CH1) - divider 2.2k/3.3k
   - Photoresistor (CH2) - light detection and recording trigger
3. Adaptive camera exposure control (PID-like smooth controller).
4. Detect recording trigger (photoresistor covered >5 seconds).
5. Process the image to generate a dual VR view.
6. Save frame to video recording (if active).
7. Display the processed image with HUD overlay.
8. Maintain target refresh rate of 18 FPS.

#### Program Termination
1. Stop recording (if active) and save file.
2. Stop the frame capture thread.
3. Shut down the camera.
4. Close the SPI connection.
5. Close the framebuffer.

## Software-Hardware Interaction
### **Camera (Picamera2)**
- Captures RGB888 images and sends them to the program.
- Processed images are displayed on the framebuffer.
- Camera settings (brightness, contrast, exposure, gain) are controlled via software.
- Adaptive exposure control responds to lighting conditions.

### **MCP3008 ADC Converter (SPI Interface)**
- Connected sensors provide analog signals converted to digital by MCP3008.
- The program reads values from MCP3008 channels via SPI.
- Sensor data is used for:
  - Battery status monitoring
  - Dangerous CO level detection
  - Adaptive camera exposure control
  - Video recording triggering

### **Framebuffer /dev/fb0**
- The processed image is converted to RGB565 format.
- The final image is written to /dev/fb0, which updates the display in real-time.
- HUD (sensor information) is overlaid on the image before writing.

## System Testing & Optimization
### **Performance Impact on Image Quality**
- Raspberry Pi Zero 2 W has limited computational power.
- Optimization techniques include reducing input resolution (320x360 per eye) and using multi-threading.
- Stable 18 FPS provides smooth image with low latency.
- Using a Raspberry Pi 4 could improve performance for higher resolution and more advanced image processing.

### **Color Processing Issues & Solutions**
- Initial color rendering issues were due to improper RGB888 to RGB565 conversion.
- Using proper OpenCV methods (cv2.COLOR_BGR2BGR565) fixed most issues.
- Some inaccuracies remain in low-light areas, requiring further contrast management.

### **FPS Optimization**
- Initial frame rate was low (~10-15 FPS), causing noticeable lag.
- Dedicated thread for image acquisition, framebuffer display optimization, and reduced sensor read frequency achieved stable 18 FPS with low latency.
- Future improvement: Utilize hardware-accelerated image encoding (h264_v4l2m2m) instead of OpenCV software processing.

## Installation & Setup

### Requirements
```bash
sudo apt update
sudo apt install python3-opencv python3-picamera2 python3-spidev python3-numpy
```

### File Transfer to Device
```bash
scp -i "key_file" -o StrictHostKeyChecking=no program.py maska@192.168.1.105:~/program.py
```

### Autostart on Boot
Create systemd service:
```bash
sudo nano /etc/systemd/system/welding-mask.service
```

Service file content:
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

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable welding-mask.service
sudo systemctl start welding-mask.service
```

### Troubleshooting Boot Issues
If system freezes during boot (e.g., at `WayVNCControlService`, `rpc-statd-notify.service`, `cups.service`, `cups-browsed.service`, `NetworkManager-dispatcher.service`), see [fix_boot_freeze.md](fix_boot_freeze.md) for detailed instructions.

**Quick fix (via SSH):**
```bash
# Disable all unnecessary services causing boot hangs
sudo systemctl disable wayvnc
sudo systemctl mask wayvnc-control.service
sudo systemctl disable rpc-statd.service
sudo systemctl mask rpc-statd-notify.service
sudo systemctl disable cups.service
sudo systemctl disable cups-browsed.service
sudo systemctl mask cups.service
sudo systemctl mask cups-browsed.service
sudo systemctl disable NetworkManager-dispatcher.service
sudo systemctl mask NetworkManager-dispatcher.service

sudo reboot
```

### **Future Enhancements**
- ✅ ~~Enable video recording~~ (implemented Dec 2025)
- Upgrade to a more powerful hardware (e.g., Raspberry Pi 4).
- Implement additional image filters for better display quality.
- Expand AR capabilities with head-tracking or environmental interaction.
- Live streaming to another device.
- Add mechanical control for camera aperture.
- Upgrade to a higher-quality camera lens.

## Technical Documentation and Schematics

![schemat_blokowy](https://github.com/user-attachments/assets/596fdb22-4aad-4948-9483-1b2a79ff850a)

![schema](https://github.com/user-attachments/assets/df591576-924b-4fb6-b2c4-a62a69f624a2)



