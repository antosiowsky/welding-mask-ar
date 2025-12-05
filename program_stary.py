import numpy as np
from picamera2 import Picamera2
import cv2
import time
from threading import Thread
import spidev

# Rozdzielczość framebuffera
fb_width, fb_height = 1920, 1080

# Debug mode: when True will print errors, show an OpenCV preview window
# and save occasional debug frames to ~/Project/debug_frames/
DEBUG_MODE = False

# Inicjalizacja SPI dla MCP3008
spi = spidev.SpiDev()
spi.open(0, 0)  # Port 0, urządzenie 0
spi.max_speed_hz = 1350000  # Maksymalna szybkość SPI

def read_adc(channel):
    """Funkcja odczytująca dane z czujnika podłączonego do MCP3008."""
    if channel < 0 or channel > 7:
        raise ValueError("Kanał ADC musi być z zakresu 0-7.")
    # Wysyłanie danych do MCP3008
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    # Odczyt danych
    result = ((adc[1] & 3) << 8) + adc[2]
    return result

class FrameProcessor:
    def __init__(self, picam2):
        self.picam2 = picam2
        self.running = True
        self.frame = None
        self.thread = Thread(target=self.capture_frames, daemon=True)
        self.thread.start()

    def capture_frames(self):
        while self.running:
            # Pobieranie klatki z kamery
            self.frame = self.picam2.capture_array()

    def stop(self):
        self.running = False
        self.thread.join()

# Ustawienia ramki i tła (obliczone tylko raz)
frame_width = int(fb_width * 0.8)  # 80% szerokości framebuffera
frame_height = int(fb_height * 0.8)  # 80% wysokości framebuffera
x_offset = (fb_width - frame_width) // 2
y_offset = (fb_height - frame_height) // 2

def air_quality(sensor_data):
    if sensor_data <= 400:
        return "good"
    elif  400<= sensor_data <= 700:
        return "bad"
    else:
        return "dangerous"


# Tworzenie czarnego tła o rozmiarze framebuffera
background_template = np.zeros((fb_height, fb_width, 3), dtype=np.uint8)

def display_on_framebuffer(image, sensor_data, light, fb_handle=None, save_debug_frame=False, dbg_frame_idx=0):
    """Wyświetlanie obrazu w ramce z wyższą rozdzielczością."""
    # Skalowanie obrazu do ramki (stała rozdzielczość)
    resized_image = cv2.resize(image, (frame_width, frame_height), interpolation=cv2.INTER_LINEAR)

    # Kopiowanie tła
    background = background_template.copy()

    # Wklejenie zmniejszonego obrazu na tło
    background[y_offset:y_offset + frame_height, x_offset:x_offset + frame_width] = resized_image

    # Dodanie wartości czujnika i naładowania baterii do obrazu
    cv2.putText(background, f'Air quality: {air_quality(sensor_data)}', (230, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(background, f'Ligtht: {light}', (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    #if light <= 130:
        #picam2.set_controls({"Brightness": 30})
    #elif light >=130:
        #picam2.set_controls({"Brightness": 100})
        #swiatlo <200 powinno byc juz przyciemniane (sprawdzone dla latarki wiec moze byc nawer <150)


    # Konwersja na RGB565, jeśli framebuffer wymaga
    try:
        # convert to the 16-bit format expected by fb0 (RGB565)
        rgb565_image = cv2.cvtColor(background, cv2.COLOR_BGR2BGR565)
    except Exception as e:
        if DEBUG_MODE:
            print('Color conversion to BGR565 failed:', e)
        # fall back to writing raw BGR bytes (may not display correctly)
        rgb565_image = background

    # Debug preview window (only works if running in an X/GUI session)
    if DEBUG_MODE:
        try:
            cv2.imshow('program_stary Preview', background)
            cv2.waitKey(1)
        except Exception:
            # no X available or display not accessible; ignore
            pass

    # Optionally save debug frame for offline inspection
    if save_debug_frame and DEBUG_MODE:
        try:
            import os
            dbg_dir = os.path.expanduser('~/Project/debug_frames')
            os.makedirs(dbg_dir, exist_ok=True)
            fname = os.path.join(dbg_dir, f'dbg_frame_{dbg_frame_idx:04d}.jpg')
            # convert to BGR for saving
            try:
                save_bgr = cv2.cvtColor(rgb565_image, cv2.COLOR_BGR2RGB) if rgb565_image.dtype == background.dtype else background
            except Exception:
                save_bgr = background
            cv2.imwrite(fname, save_bgr)
        except Exception as e:
            if DEBUG_MODE:
                print('Failed to save debug frame:', e)

    # Zapis obrazu do framebuffera
    try:
        if fb_handle is not None:
            # use cached handle
            fb_handle.seek(0)
            fb_handle.write(rgb565_image.tobytes())
            fb_handle.flush()
        else:
            with open('/dev/fb0', 'wb') as fb:
                fb.write(rgb565_image.tobytes())
    except Exception as e:
        # Always print framebuffer write errors when debugging; otherwise ignore
        if DEBUG_MODE:
            print('Framebuffer write error:', e)

# Inicjalizacja kamery
picam2 = Picamera2()
camera_controls = {
    "Sharpness": 1.0,  # Wyostrzenie obrazu
    "Contrast": 1.0,   # Zwiększenie kontrastu
    "Brightness": 100,  # Jasność (wartości od 0 do 100)
    "Saturation": 1.0, # Nasycenie kolorów
    "ExposureTime": 100,  # Czas naświetlania
    "AnalogueGain": 6.0,
    "NoiseReductionMode": "HighQuality"
}
picam2.set_controls(camera_controls)
picam2.configure(picam2.create_preview_configuration(main={"size": (fb_width // 2, fb_height), "format": "RGB888"}, raw={"size": (4056,3040)}))
picam2.start()

# Uruchomienie wątku przetwarzającego klatki
frame_processor = FrameProcessor(picam2)
# Open framebuffer once (cached handle) to avoid reopening each frame
fb_handle = None
try:
    fb_handle = open('/dev/fb0', 'wb', buffering=0)
except Exception:
    fb_handle = None

dbg_frame_idx = 0

try:
    while True:
        # Pobieranie klatki z wątku
        frame = frame_processor.frame

        if frame is not None:
            # Pobranie danych z czujnika (np. z kanału 0)
            sensor_value = read_adc(0)
            # Pobranie danych z czujnika światła (kanał 7)
            light_value = read_adc(7)

            # Tworzenie obrazu VR (podwójny obraz obok siebie)
            double_frame = np.hstack((frame, frame))

            # Wyświetlenie obrazu w framebufferze wraz z danymi z czujnika i baterii
            display_on_framebuffer(double_frame, sensor_value, light_value, fb_handle=fb_handle, dbg_frame_idx=dbg_frame_idx)
            dbg_frame_idx += 1

        # Kontrola FPS (~30 klatek/s)
        time.sleep(0.01)
finally:
    frame_processor.stop()
    picam2.stop()
    spi.close()  # Zamknięcie połączenia SPI
    if fb_handle:
        try:
            fb_handle.close()
        except Exception:
            pass