# AR Welding Helmet (Maska Spawalnicza z AR) 
### Augmented Reality system supporting electric arc welding based on Video Pass-Through technology.

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%20Zero%202W-red)
![Hardware](https://img.shields.io/badge/Hardware-Custom%20PCB-green)
![Status](https://img.shields.io/badge/Status-Prototype%20Completed-success)

## 📖 Abstract
**Bachelor's Thesis Project**

The aim of this project was to design and construct a welding helmet utilizing **Augmented Reality (AR)** technology in **Video Pass-Through** mode. The system eliminates the risk of flash blindness by replacing the traditional optical path with a digital vision system using a **Global Shutter camera**.

The device features a custom-made PCB, a hybrid power supply with **Energy Harvesting** (solar panel), and environmental sensors (gas, light). The software runs on a **Raspberry Pi Zero 2 W**, utilizing direct framebuffer access to achieve low-latency stereoscopic vision.

---

## ⚙️ Hardware Architecture

### Core Components
*   **SBC:** Raspberry Pi Zero 2 W
*   **Camera:** Raspberry Pi Global Shutter Camera (Sony IMX296) + ND 2-1000 Filter
*   **Display:** 5.5" HDMI AMOLED (1920x1080)
*   **ADC:** MCP3008 (SPI interface)

### Sensors & Power
*   **Gas Sensor:** MQ-07 (Carbon Monoxide)
*   **Light Sensor:** Photoresistor (Trigger for AGC)
*   **Energy Harvesting:** Polycrystalline Solar Panel
*   **Power:** Li-Ion 18650 Cells + BMS

### Custom PCB
The motherboard was designed in **KiCad/Fusion 360** and manufactured using a custom **laser ablation method** and chemical etching.
<!-- TU WRZUĆ ZDJĘCIE PCB (ZDJĘCIE D Z PRACY) -->
![Custom PCB Process](media/images/pcb_final.jpg)

---

## 🛠️ Software & Algorithms

The control software is written in **Python** and optimized for the limited resources of the RPi Zero 2 W.

*   **Direct Framebuffer Access:** Writing directly to `/dev/fb0` to bypass X11 overhead.
*   **Adaptive Exposure Control (AEC):** Custom PID-like algorithm to adjust exposure time and gain in <100ms during arc ignition.
*   **Multithreading:** Separated capture, processing, and rendering threads.
*   **Stereoscopy:** Split-screen rendering for VR lens optics.

### Requirements
```text
opencv-python-headless
picamera2
spidev
numpy
```
# 🛡️ Smart Welding Helmet with AR HUD

Projekt inteligentnej przyłbicy spawalniczej wyposażonej w wyświetlacz przezierny (HUD) oraz zaawansowane systemy monitorowania bezpieczeństwa.

---

## 📸 Gallery & Demo

### 1. The Prototype
Poniższe zdjęcia przedstawiają fizyczną konstrukcję maski oraz integrację systemów elektronicznych.

| **Front View** | **Internal Electronics** |
| :---: | :---: |
| ![Front View](media/images/mask_front.jpg) | ![Internal Electronics](media/images/mask_back.jpg) |

### 2. AR HUD Interface (Scenarios)
Wizualizacja danych wyświetlanych bezpośrednio na szybce przyłbicy w różnych warunkach pracy.

| **Welding Arc (Active AGC)** | **Gas Alarm (Safety)** |
| :---: | :---: |
| ![Welding Arc](media/images/hud_welding.jpg) | ![Gas Alarm](media/images/hud_alarm.jpg) |

### 3. Video Demo
Kliknij w poniższą miniaturę, aby obejrzeć demonstrację wideo na YouTube:

[![Watch the video](https://img.youtube.com/vi/YOUR_VIDEO_ID_HERE/0.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID_HERE)

> **Note:** Jeśli nie masz linku do YouTube, możesz pobrać plik wideo bezpośrednio z repozytorium: `media/video/demo.mp4`.

---

## 🏗️ Mechanical Design

Cała konstrukcja mechaniczna, w tym obudowy elektroniki i uchwyty, została zaprojektowana w programie **Autodesk Fusion 360**. Modele zostały zoptymalizowane pod kątem druku 3D z materiałów **PET-G** oraz **PLA**.

![CAD Model](media/images/cad_model.png)

---

## 📄 License & Information

Ten projekt jest oprogramowaniem open-source udostępnianym na licencji **MIT**.

* **Author:** Jakub Antonowicz
* **University:** Politechnika Śląska (Silesian University of Technology)
* **
