# ENG BELOW! 

# Maska do spawania AR / Welding AR System Using Raspberry Pi Zero 2 W / [PL/ENG]


## Temat Projektu
Projekt dotyczy stworzenia systemu AR wykorzystującego Raspberry Pi Zero 2 W, kamerę oraz wyświetlacz 5,5 cala (1920x1080). System wyświetla na żywo obraz z kamery podzielony na dwie równe połowy, co umożliwia używanie wyświetlacza jako gogli AR.

## Opis Funkcji Urządzenia
- Pobieranie obrazu z kamery w czasie rzeczywistym.
- Przetwarzanie obrazu w celu poprawienia jakości.
- Wyświetlanie obrazu na ekranie podzielonym na dwie części.
- Odczyt danych z czujnika jakości powietrza.
- Odczyt poziomu oświetlenia i dostosowanie ekspozycji kamery.

## Uzasadnienie Wyboru Elementów Elektronicznych
- **Raspberry Pi Zero 2 W** - kompaktowa platforma zdolna do obsługi kamer i wyświetlaczy.
- **Kamera Raspberry PI Global Shutter Camera** - kompatybilna z Raspberry Pi, zapewnia niskie opóźnienia.
- **Wyświetlacz 5,5 cala 1920x1080** - pozwala na realistyczne wrażenia AR.
- **MCP3008 (ADC)** - pozwala na odczyt danych z analogowych czujników.

## Użyte Narzędzia
- **Python 3** - język programowania do obsługi kamery i czujników.
- **OpenCV** - biblioteka do przetwarzania obrazu.
- **Spidev** - obsługa magistrali SPI dla czujnika MCP3008.

## Algorytm Oprogramowania

### Inicjalizacja systemu
- Ustawienie rozdzielczości framebuffera.
- Inicjalizacja interfejsu SPI do komunikacji z przetwornikiem ADC MCP3008.
- Konfiguracja kamery Picamera2.
- Uruchomienie wątku odpowiedzialnego za przechwytywanie klatek w czasie rzeczywistym.

### Pętla główna programu
- Pobranie aktualnej klatki obrazu z kamery.
- Odczyt wartości z czujników podłączonych do MCP3008 (np. czujnika jakości powietrza i czujnika światła).
- Przetwarzanie obrazu w celu wygenerowania podwójnego widoku VR.
- Wyświetlenie obrazu na framebufferze wraz z informacjami z czujników.
- Kontrola częstotliwości odświeżania (ok. 30 FPS).

### Zakończenie programu
- Zatrzymanie wątku przechwytywania klatek.
- Zatrzymanie kamery.
- Zamknięcie połączenia SPI.

## Opis interakcji oprogramowania z układem elektronicznym

### Kamera Picamera2
- Kamera przechwytuje obraz w formacie RGB888 i przekazuje go do programu.
- Obraz jest przetwarzany i wyświetlany na framebufferze.
- Program steruje ustawieniami kamery (jasność, kontrast, czas naświetlania).

### Przetwornik ADC MCP3008 (SPI)
- Czujniki są podłączone do MCP3008, który przekształca ich sygnał analogowy na cyfrowy.
- Program odczytuje wartości z kanałów MCP3008 przez interfejs SPI.
- Dane z czujników są wykorzystywane do analizy jakości powietrza i natężenia światła.

### Framebuffer /dev/fb0
- Obraz przetworzony w programie jest konwertowany do formatu RGB565.
- Wynikowy obraz jest zapisywany bezpośrednio do pliku /dev/fb0, który steruje wyświetlaczem.

# Wnioski z Uruchamiania i Testowania

## Wpływ wydajności sprzętu na jakość obrazu
Raspberry Pi Zero 2 W, mimo swojej kompaktowości, ma ograniczone zasoby obliczeniowe. Wydajność została zoptymalizowana poprzez zmniejszenie rozdzielczości obrazu wejściowego oraz zastosowanie przetwarzania wielowątkowego. Jednak przy wyższej jakości obrazu mogłyby pojawiać się opóźnienia.

Potencjalnym usprawnieniem byłoby użycie Raspberry Pi 4 lub innego mocniejszego układu, co pozwoliłoby na bardziej zaawansowane przetwarzanie obrazu.

## Problemy z kolorami i ich rozwiązanie
Początkowe problemy z odwzorowaniem kolorów wynikały z błędnej konwersji RGB888 do RGB565. Użycie alternatywnych metod przetwarzania kolorów w OpenCV pozwoliło na poprawienie jakości obrazu. Nadal występują drobne przekłamania w bardzo ciemnych obszarach, co można poprawić poprzez lepsze zarządzanie kontrastem.

## Optymalizacja FPS
Początkowo liczba klatek na sekundę była niska (około 10–15 FPS), co powodowało efekt „lag” przy ruchu kamery. Zastosowanie wątku do akwizycji obrazu oraz poprawa sposobu wyświetlania klatek pozwoliły na uzyskanie stabilnych 25–30 FPS.

Możliwości dalszej poprawy: wykorzystanie sprzętowego kodowania obrazu zamiast programowego przetwarzania przez OpenCV.

# Potencjalne przyszłe ulepszenia
- Zastosowanie mocniejszego sprzętu (np. Raspberry Pi 4) w celu poprawy wydajności.
- Dodanie filtrów obrazu do lepszego dostosowania jakości wyświetlania.
- Rozszerzenie funkcjonalności AR poprzez śledzenie ruchu głowy lub interakcję z otoczeniem.
- Możliwość nagrywania wideo lub transmisji obrazu na żywo do innego urządzenia.
- Dodanie elementu mechanicznego obracającego pokrętłem przysłony obiektywu.
- Zakup lepszego obiektywu.

![schemat_blokowy](https://github.com/user-attachments/assets/596fdb22-4aad-4948-9483-1b2a79ff850a)

![schemat](https://github.com/user-attachments/assets/9bff36c3-9561-4d6e-b886-7f356c689b2f)

# ENG

# Welding AR System Using Raspberry Pi Zero 2 W

## Project Overview
This project involves creating an Augmented Reality (AR) system using a Raspberry Pi Zero 2 W, a camera, and a 5.5-inch display (1920x1080). The system captures real-time video from the camera and splits it into two equal halves, enabling the display to function as AR goggles.

## Features
- Real-time video capture from the camera.
- Image processing for quality enhancement.
- Splitting the video into two sections for VR-like visualization.
- Air quality sensor data reading.
- Light intensity measurement and camera exposure adjustment.

## Hardware Components
- **Raspberry Pi Zero 2 W** – A compact platform capable of handling cameras and displays.
- **Raspberry Pi Global Shutter Camera** – Provides low latency and is compatible with Raspberry Pi.
- **5.5-inch 1920x1080 Display** – Offers a high-resolution AR experience.
- **MCP3008 (ADC Converter)** – Reads data from analog sensors.

## Software & Tools
- **Python 3** – Main programming language for device and sensor management.
- **OpenCV** – Library for image processing.
- **Spidev** – SPI interface library for MCP3008 communication.

### Software Algorithm
#### System Initialization
1. Set framebuffer resolution.
2. Initialize SPI interface for ADC MCP3008 communication.
3. Configure the Picamera2 camera.
4. Start a thread for real-time frame capture.

#### Main Program Loop
1. Capture the latest frame from the camera.
2. Read sensor data from MCP3008 (air quality and light intensity sensors).
3. Process the image to generate a dual VR view.
4. Display the processed image along with sensor information.
5. Maintain an approximate refresh rate of 30 FPS.

#### Program Termination
1. Stop the frame capture thread.
2. Shut down the camera.
3. Close the SPI connection.

## Software-Hardware Interaction
### **Camera (Picamera2)**
- Captures RGB888 images and sends them to the program.
- Processed images are displayed on the framebuffer.
- Camera settings (brightness, contrast, exposure) are controlled via software.

### **MCP3008 ADC Converter (SPI Interface)**
- Connected sensors provide analog signals converted to digital by MCP3008.
- The program reads air quality and light intensity values from MCP3008 via SPI.
- Data is displayed on the screen.

### **Framebuffer /dev/fb0**
- The processed image is converted to RGB565 format.
- The final image is written to /dev/fb0, which updates the display in real-time.

## System Testing & Optimization
### **Performance Impact on Image Quality**
- Raspberry Pi Zero 2 W has limited computational power.
- Optimization techniques include reducing input resolution and using multi-threading.
- Using a Raspberry Pi 4 could improve performance for more advanced image processing.

### **Color Processing Issues & Solutions**
- Initial color rendering issues were due to improper RGB888 to RGB565 conversion.
- OpenCV-based color processing fixed most issues.
- Some inaccuracies remain in low-light areas, requiring further contrast management.

### **FPS Optimization**
- Initial frame rate was low (~10-15 FPS), causing noticeable lag.
- Multi-threaded frame capture and optimized rendering improved FPS to ~25-30.
- Future improvement: Utilize hardware-accelerated image encoding.

### **Future Enhancements**
- Upgrade to a more powerful hardware (e.g., Raspberry Pi 4).
- Implement additional image filters for better display quality.
- Expand AR capabilities with head-tracking or environmental interaction.
- Enable video recording or live streaming.
- Add mechanical control for camera aperture.
- Upgrade to a higher-quality camera lens.

