#!/usr/bin/env python3
"""
AR Welding Mask - Main Program
Real-time camera feed with sensor overlay for AR goggles display
Displays dual-view (VR mode) with battery, air quality (MQ-07), and light level info
"""

import numpy as np
from picamera2 import Picamera2
import cv2
import os
import time
from threading import Thread, Lock
import spidev
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

# Framebuffer resolution (display)
FB_WIDTH, FB_HEIGHT = 1920, 1080

# Camera preview size (half-width for dual view) - reduced for better FPS on RPi Zero
CAMERA_WIDTH = 320  # Ultra-low res for speed (320x360 per eye = 640x360 dual)
CAMERA_HEIGHT = 360

# SPI configuration for MCP3008
SPI_BUS = 0
SPI_DEVICE = 0
SPI_SPEED = 1350000  # 1.35 MHz

# MCP3008 channel mapping (as per sensor_test.py)
CH_BATTERY = 0      # 18650 battery with 10k/20k voltage divider
CH_MQ07 = 1         # MQ-07 CO sensor with 2.2k/3.3k voltage divider
CH_LIGHT = 2        # Photoresistor with 10k resistor

# Display settings
DISPLAY_SCALE = 0.8  # Scale factor for image frame within framebuffer (80% of screen)
DEBUG_MODE = True   # Set to True to print FPS and sensor values to console and show cv2 preview

# Camera exposure/brightness adjustment based on light
LIGHT_ADJUST_ENABLED = True
LIGHT_ADJUST_INTERVAL = 0.15    # Adjust every 0.15s (very fast adaptive response)
LIGHT_THRESHOLD_DIM = 200       # Below this: increase exposure
LIGHT_THRESHOLD_BRIGHT = 700    # Above this: decrease exposure

# Adaptive gain controller (PID-like smooth adjustment instead of threshold jumps)
ADAPTIVE_GAIN_ENABLED = True
GAIN_TARGET_LIGHT = 450          # Target light level for neutral gain
GAIN_MIN = 1.0                   # Minimum gain
GAIN_MAX = 16.0                  # Maximum gain
GAIN_RATE = 0.15                # Smooth adjustment rate (0.0-1.0, lower = smoother)
EXPOSURE_TIME_MIN = 1000         # Min exposure time (1ms) - reduce latency
EXPOSURE_TIME_MAX = 20000        # Max exposure time (20ms)

# Performance settings
TARGET_FPS = 18                 # Target frame rate (reduced for sensor reads + larger display)
FRAMEBUFFER_CACHE = None        # Cache framebuffer file handle
FRAME_TIME_BUDGET = 1.0 / TARGET_FPS  # Time budget per frame (seconds)
MIN_FRAME_TIME = 0.003  # Minimum sleep to avoid CPU spin

# ============================================================================
# SENSOR CALIBRATION (from sensor_test.py)
# ============================================================================

VREF = 3.3  # MCP3008 reference voltage

def read_adc(channel):
    """
    Read ADC value from MCP3008 channel.
    
    Args:
        channel (int): ADC channel (0-7)
        
    Returns:
        int: Digital value (0-1023)
    """
    if channel < 0 or channel > 7:
        return -1
    
    # MCP3008 requires 3 bytes: start bit, single-ended mode, channel selection
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def calculate_battery_voltage(adc_value):
    """
    Calculate battery voltage from ADC reading.
    Voltage divider: 10kΩ to GND, 20kΩ to battery
    Vout = Vin * (10k / 30k) => Vin = Vout * 3
    
    Args:
        adc_value (int): ADC reading (0-1023)
        
    Returns:
        tuple: (voltage, status_text, is_critical)
    """
    v_measured = (adc_value / 1023.0) * VREF
    v_battery = v_measured * 3.0
    
    # Battery status
    if v_battery > 4.1:
        status = "Full"
        critical = False
    elif v_battery > 3.7:
        status = "Good"
        critical = False
    elif v_battery > 3.4:
        status = "Medium"
        critical = False
    elif v_battery > 3.0:
        status = "Low"
        critical = True
    else:
        status = "Critical"
        critical = True
    
    return v_battery, status, critical

def calculate_mq07_status(adc_value):
    """
    Calculate MQ-07 CO sensor status from ADC reading.
    Voltage divider: 2.2kΩ to GND, 3.3kΩ to sensor
    Vout = Vin * (2.2k / 5.5k) => Vin = Vout * 2.5
    
    Calibration:
    - 0.8V or less: Good (OK)
    - 1.4V: Acceptable (warning)
    - 2.8V+: Dangerous (alarm)
    
    Args:
        adc_value (int): ADC reading (0-1023)
        
    Returns:
        tuple: (voltage, status_text, is_dangerous)
    """
    v_measured = (adc_value / 1023.0) * VREF
    v_sensor = v_measured * 2.5
    
    # Air quality status - removed "Very Good"
    if v_sensor <= 0.8:
        status = "Good"
        dangerous = False
    elif v_sensor < 1.4:
        status = "Acceptable"
        dangerous = False
    elif v_sensor < 2.8:
        status = "Warning"
        dangerous = True
    else:
        status = "DANGER!"
        dangerous = True
    
    return v_sensor, status, dangerous

def calculate_light_level(adc_value):
    """
    Calculate light level from photoresistor ADC reading.
    
    Calibration:
    - 0: darkness
    - 602: natural light
    - 950: flashlight (very bright)
    
    Args:
        adc_value (int): ADC reading (0-1023)
        
    Returns:
        tuple: (adc_value, status_text)
    """
    # Light status based on calibration
    if adc_value < 100:
        status = "Dark"
    elif adc_value < 400:
        status = "Dim"
    elif adc_value < 750:
        status = "Normal"
    elif adc_value < 950:
        status = "Bright"
    else:
        status = "Very Bright"
    
    return adc_value, status

# ============================================================================
# FRAME CAPTURE THREAD
# ============================================================================

class FrameProcessor:
    """Thread-safe camera frame capture."""
    
    def __init__(self, picam2):
        self.picam2 = picam2
        self.running = True
        self.frame = None
        self.lock = Lock()
        self.thread = Thread(target=self._capture_frames, daemon=True)
        self.thread.start()
    
    def _capture_frames(self):
        """Continuously capture frames from camera."""
        while self.running:
            try:
                captured = self.picam2.capture_array()
                with self.lock:
                    self.frame = captured
            except Exception as e:
                print(f"Frame capture error: {e}")
                time.sleep(0.1)
    
    def get_frame(self):
        """Get the latest captured frame (thread-safe)."""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def stop(self):
        """Stop the capture thread."""
        self.running = False
        self.thread.join(timeout=2.0)

# ============================================================================
# DISPLAY RENDERING
# ============================================================================

# Pre-calculate frame positioning
frame_width = int(FB_WIDTH * DISPLAY_SCALE)
frame_height = int(FB_HEIGHT * DISPLAY_SCALE)
x_offset = (FB_WIDTH - frame_width) // 2
y_offset = (FB_HEIGHT - frame_height) // 2

# Create background template (reused to avoid allocations)
background_template = np.zeros((FB_HEIGHT, FB_WIDTH, 3), dtype=np.uint8)

# Pre-allocate RGB565 buffer (reused for framebuffer writes)
rgb565_buffer = np.zeros((FB_HEIGHT, FB_WIDTH), dtype=np.uint16)

def render_osd(image, battery_voltage, battery_status, battery_critical,
               mq07_voltage, mq07_status, mq07_dangerous,
               light_value, light_status):
    """
    Render on-screen display (OSD) with clean layout.
    Shows battery, air quality, light level. Red border if danger.
    
    Args:
        image (ndarray): Image to render text on
        battery_voltage (float): Battery voltage
        battery_status (str): Battery status text
        battery_critical (bool): Battery critical flag
        mq07_voltage (float): MQ-07 voltage
        mq07_status (str): Air quality status
        mq07_dangerous (bool): Air quality danger flag
        light_value (int): Light ADC value
        light_status (str): Light status text
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.9  # Larger font for better visibility
    thickness = 2
    
    # Battery info (top-left)
    battery_color = (0, 0, 255) if battery_critical else (0, 255, 0)
    cv2.putText(image, f"Bat: {battery_voltage:.1f}V ({battery_status})",
                (20, 50), font, font_scale, battery_color, thickness, cv2.LINE_AA)
    
    # Air quality (top-left, below battery) - no voltage display
    air_color = (0, 0, 255) if mq07_dangerous else (0, 255, 0)
    cv2.putText(image, f"Air: {mq07_status}",
                (20, 100), font, font_scale, air_color, thickness, cv2.LINE_AA)
    
    # Light level info hidden (commented out)
    
    # RED BORDER if danger
    if mq07_dangerous:
        cv2.rectangle(image, (5, 5), (FB_WIDTH - 5, FB_HEIGHT - 5), (0, 0, 255), 8)

def display_on_framebuffer(double_frame, battery_voltage, battery_status, battery_critical,
                            mq07_voltage, mq07_status, mq07_dangerous,
                            light_value, light_status, fb_handle=None):
    """
    Render dual-view frame with OSD to framebuffer.
    Optimized: reuses buffers, minimal copies, cached file handle, fast resize.
    
    Args:
        double_frame (ndarray): Dual camera view (side-by-side)
        battery_voltage, battery_status, battery_critical: Battery info
        mq07_voltage, mq07_status, mq07_dangerous: Air quality info
        light_value, light_status: Light level info
        fb_handle: Cached framebuffer file handle (optional)
    """
    global rgb565_buffer
    
    # Resize to fit frame area (use INTER_NEAREST for maximum speed on embedded)
    resized_image = cv2.resize(double_frame, (frame_width, frame_height), interpolation=cv2.INTER_NEAREST)

    # Copy background and place resized image
    background = background_template.copy()
    background[y_offset:y_offset + frame_height, x_offset:x_offset + frame_width] = resized_image

    # Render OSD using existing renderer
    try:
        render_osd(background, battery_voltage, battery_status, battery_critical,
                   mq07_voltage, mq07_status, mq07_dangerous,
                   light_value, light_status)
    except Exception:
        # fallback: minimal text if render_osd fails
        try:
            cv2.putText(background, f'Air: {mq07_status}', (230, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(background, f'Light: {light_value}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        except Exception:
            pass

    # Convert to RGB565 (optimized: reuse buffer when possible)
    try:
        rgb565_image = cv2.cvtColor(background, cv2.COLOR_BGR2BGR565)
    except Exception as e:
        if DEBUG_MODE:
            print('DEBUG: Color conversion to BGR565 failed:', e)
        rgb565_image = background

    # Write to framebuffer (use cached handle if provided)
    try:
        if fb_handle is not None:
            fb_handle.seek(0)
            fb_handle.write(rgb565_image.tobytes())
            fb_handle.flush()
        else:
            with open('/dev/fb0', 'wb') as fb:
                fb.write(rgb565_image.tobytes())
    except Exception as e:
        if DEBUG_MODE:
            print('DEBUG: Framebuffer write error:', e)

# ============================================================================
# CAMERA CONTROL
# ============================================================================

# Global state for adaptive gain controller
adaptive_gain_state = {
    'current_gain': 6.0,
    'current_exposure': 10000,
    'last_update': 0
}

def adjust_camera_exposure(picam2, light_value):
    """
    Adaptive gain controller (PID-like) for smooth, flicker-free exposure.
    Replaces threshold-based jumps with smooth interpolation.
    Reduces latency with lower ExposureTime and NoiseReduction disabled during bright.
    
    Args:
        picam2: Picamera2 instance
        light_value (int): Light ADC value
    """
    if not LIGHT_ADJUST_ENABLED:
        return
    
    try:
        # Adaptive gain: smooth controller based on distance from target
        error = GAIN_TARGET_LIGHT - light_value
        
        # Calculate target gain (proportional controller)
        # error = +300 (too dark) => high gain
        # error = 0 (perfect) => medium gain
        # error = -300 (too bright) => low gain
        gain_normalize = error / 300.0  # Normalize error to [-1, 1] range
        
        # Target gain: mid-range at neutral, scales toward extremes
        target_gain = 6.0 + (gain_normalize * 5.0)  # 1-11 range
        target_gain = max(GAIN_MIN, min(GAIN_MAX, target_gain))  # Clamp
        
        # Smooth interpolation toward target (prevents jitter)
        new_gain = adaptive_gain_state['current_gain'] * (1.0 - GAIN_RATE) + target_gain * GAIN_RATE
        new_gain = max(GAIN_MIN, min(GAIN_MAX, new_gain))
        
        # Adaptive exposure time (reduce latency by lowering exposure in bright, keeping it higher in dark)
        if light_value > 600:  # Bright: minimal exposure for low latency
            target_exposure = EXPOSURE_TIME_MIN + 1000  # ~2-3ms
        elif light_value > 400:  # Normal: medium exposure
            target_exposure = 8000  # ~8ms
        elif light_value > 200:  # Dim: longer exposure
            target_exposure = 12000  # ~12ms
        else:  # Very dark: maximum exposure
            target_exposure = EXPOSURE_TIME_MAX  # ~20ms
        
        # Smooth exposure adjustment
        new_exposure = int(adaptive_gain_state['current_exposure'] * 0.8 + target_exposure * 0.2)
        new_exposure = max(EXPOSURE_TIME_MIN, min(EXPOSURE_TIME_MAX, new_exposure))
        
        # Only update if change is significant (avoid redundant calls)
        if abs(new_gain - adaptive_gain_state['current_gain']) > 0.1 or \
           abs(new_exposure - adaptive_gain_state['current_exposure']) > 500:
            
            controls = {
                "AnalogueGain": new_gain,
                "ExposureTime": new_exposure,
                "Brightness": -0.05 if light_value > 700 else (0.05 if light_value < 200 else 0.0),
                "Contrast": 1.0 if light_value > 700 else (1.4 if light_value < 200 else 1.2)
            }
            
            picam2.set_controls(controls)
            adaptive_gain_state['current_gain'] = new_gain
            adaptive_gain_state['current_exposure'] = new_exposure
            
            if DEBUG_MODE and light_value % 30 == 0:  # Log every ~30 samples
                print(f"Adaptive: light={light_value} -> gain={new_gain:.1f} exp={new_exposure}µs")
    
    except Exception as e:
        if DEBUG_MODE:
            print(f"Camera control error: {e}")

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main program loop."""
    global spi
    
    print("Initializing AR Welding Mask System...")
    
    # Initialize SPI for MCP3008
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    spi.max_speed_hz = SPI_SPEED
    print("SPI initialized")
    
    # Initialize camera - optimized for low latency spawanie
    picam2 = Picamera2()
    camera_config = {
        "Sharpness": 1.0,
        "Contrast": 1.2,
        "Brightness": 0.0,
        "Saturation": 1.0,
        "ExposureTime": 8000,           # Lower initial exposure (8ms) for responsiveness
        "AnalogueGain": 6.0
    }
    picam2.set_controls(camera_config)
    
    # Configure camera for dual-view (half-width per eye)
    picam2.configure(picam2.create_preview_configuration(
        main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT), "format": "RGB888"}
    ))
    picam2.start()
    print("Camera initialized")
    
    # Start frame capture thread
    frame_processor = FrameProcessor(picam2)
    print("Frame processor started")
    
    # FPS tracking
    fps_counter = 0
    fps_start_time = time.time()
    last_exposure_adjust = 0
    frame_counter = 0
    
    # Cache framebuffer file handle (avoid reopening every frame)
    fb_handle = None
    try:
        fb_handle = open('/dev/fb0', 'wb', buffering=0)
        print('DEBUG: opened /dev/fb0 (cached handle)')
    except Exception as e:
        print('DEBUG: could not open /dev/fb0 (will try per-frame). Error:', e)
        fb_handle = None
    
    # Cached sensor values (update every other frame to reduce SPI overhead)
    battery_v, battery_st, battery_crit = 0.0, "Unknown", False
    mq07_v, mq07_st, mq07_danger = 0.0, "Unknown", False
    light_val, light_st = 0, "Unknown"
    
    print("Main loop started. Press Ctrl+C to exit.")
    try:
        while True:
            frame_start = time.time()
            frame_counter += 1

            # Get latest frame (use direct attribute for compatibility)
            frame = frame_processor.frame
            if frame is None:
                # Sleep minimally if no frame yet (avoid busy-wait)
                time.sleep(MIN_FRAME_TIME)
                continue

            # Read sensors every 2nd frame (compromise: responsiveness vs FPS)
            if frame_counter % 2 == 0:
                try:
                    battery_adc = read_adc(CH_BATTERY)
                    mq07_adc = read_adc(CH_MQ07)
                    light_adc = read_adc(CH_LIGHT)

                    # Calculate sensor values
                    battery_v, battery_st, battery_crit = calculate_battery_voltage(battery_adc)
                    mq07_v, mq07_st, mq07_danger = calculate_mq07_status(mq07_adc)
                    light_val, light_st = calculate_light_level(light_adc)
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"Sensor read error: {e}")

            # Adjust camera exposure periodically (reduce frequency to avoid flicker)
            if time.time() - last_exposure_adjust > LIGHT_ADJUST_INTERVAL:
                adjust_camera_exposure(picam2, light_val)
                last_exposure_adjust = time.time()

            # Create dual-view (same image side-by-side)
            double_frame = np.hstack((frame, frame))

            # Display on framebuffer with OSD (use cached handle)
            try:
                display_on_framebuffer(double_frame, battery_v, battery_st, battery_crit,
                                       mq07_v, mq07_st, mq07_danger,
                                       light_val, light_st, fb_handle)
            except Exception as e:
                if DEBUG_MODE:
                    print(f"Display error: {e}")

            # FPS tracking and timing
            fps_counter += 1
            elapsed_fps = time.time() - fps_start_time
            if elapsed_fps >= 1.0:
                fps = fps_counter / elapsed_fps
                if DEBUG_MODE:
                    print(f"FPS: {fps:.1f} | Battery: {battery_v:.2f}V ({battery_st}) | "
                          f"Air: {mq07_st} ({mq07_v:.2f}V) | Light: {light_st} ({light_val})")
                fps_counter = 0
                fps_start_time = time.time()

            # Frame time regulation: sleep to maintain target FPS
            frame_elapsed = time.time() - frame_start
            frame_sleep = FRAME_TIME_BUDGET - frame_elapsed
            if frame_sleep > MIN_FRAME_TIME:
                time.sleep(frame_sleep)
            elif frame_sleep > 0:
                # Very small sleep to avoid busy-wait
                time.sleep(MIN_FRAME_TIME)

    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"Error in main loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("Cleaning up...")
        frame_processor.stop()
        picam2.stop()
        spi.close()
        if fb_handle:
            fb_handle.close()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
