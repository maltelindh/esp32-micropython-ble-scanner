# esp32-micropython-ble-scanner

Scans for nearby BLE devices and publishes results to an MQTT broker. Designed to be paired with a centralized server (e.g., Node.js app) that handles the incoming BLE data. Supports optional OTA updates for managing multiple ESP32 devices.

## Architecture

- **ESP32 Device**: Runs this firmware - scans BLE devices and publishes to MQTT
- **MQTT Broker**: Central message hub (e.g., Mosquitto)
- **Centralized Server**: Consumes BLE data from MQTT and handles business logic
- **OTA Support**: Update multiple ESP32s in the field without physical access

## Hardware

- ESP32 DEVKIT board

## Prerequisites (Windows)**Serial Driver Installation:**
Make sure you have installed the correct serial driver for your ESP32. My ESP32 WROOM board uses the CP2102 chip, driver for this can be found here:
- https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers?tab=downloads

**MicroPython Firmware:**
Follow the official MicroPython installation guide:
- https://docs.micropython.org/en/latest/esp32/tutorial/intro.html

## Setup

1. Install dependencies:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. (Optional) If connection to ESP32 fails, edit the `.bat` files and change `MPREMOTE_PORT=auto` to your COM port (e.g., `MPREMOTE_PORT=COM5`)

3. Configure credentials in `src/secrets.py`:
```python
WIFI_SSID = "your_ssid"
WIFI_PASSWORD = "your_password"
MQTT_BROKER = "192.168.x.x"
MQTT_PORT = 1883
MQTT_USER = "user"
MQTT_PASSWORD = "password"

# OTA Updates: URL to fetch updates from
# Default points to official GitHub repository
# Change to your own hosting URL or set to remove to disable
UPDATE_URL = "https://raw.githubusercontent.com/maltelindh/esp32-micropython-ble-scanner/main/src"
```

4. Flash MicroPython firmware to ESP32

5. Deploy files:
```bash
deploy.bat
```

6. Open console:
```bash
console.bat
```

7. Sometimes you might have to press the **EN** or **RST** button on the ESP32 to restart and view program log output

## Utilities

- `deploy.bat` - Deploy application files to ESP32
- `console.bat` - Open serial console to view logs
- `erase_esp32.bat` - Remove all files from ESP32

## Features

- **BLE Scanning**: Discovers nearby BLE devices and extracts service UUIDs
- **MQTT Publishing**: Sends scan results to MQTT broker in batches
- **OTA Updates** (Optional): Downloads and applies firmware updates via HTTP
- **Version Control**: Only updates if remote version differs from local

## MQTT Topics

- `esp32/ble/scan` - Published scan results (contains device list with UUIDs)
- `esp32/ota` - (Optional) Control OTA updates:
  - `{"enabled": true}` - Start checking for updates every 10 minutes
  - `{"enabled": false}` - Stop checking for updates
  - `{"url": "http://your-url/src"}` - Change UPDATE_URL and enable OTA
  - `{"url": ""}` - Disable OTA by clearing URL

## OTA Updates (Optional Feature)

If `UPDATE_URL` is configured in secrets.py:
- ESP32 automatically checks for updates every 10 minutes
- Compares local `version.json` with remote version
- If versions differ, automatically downloads and applies updates
- Files are downloaded with `_new` suffix and renamed by `boot.py` on reboot
- `boot.py` itself cannot be updated (protected)

**Configuration Options:**
- **Default**: Points to official GitHub repository
- **Custom Hosting**: Change `UPDATE_URL` to your own server
- **Disable OTA**: Set `UPDATE_URL = ""` in secrets.py

**Runtime Control via MQTT:**
You can control OTA at runtime using the `esp32/ota` topic:
```json
{"enabled": true}          // Start checking every 10 minutes
{"enabled": false}         // Stop checking (pause OTA)
{"url": "http://your-server/src"}  // Change URL and enable
{"url": ""}                // Disable OTA
```

## Project Structure

```
src/
  boot.py          - Startup, WiFi connection, file updates
  main.py          - Application orchestrator
  ble.py           - BLE scanning
  mqtt.py          - MQTT communication
  updater.py       - OTA update handler (checks every 10 min if enabled)
  secrets.py       - Configuration (WiFi, MQTT, UPDATE_URL optional)
  version.json     - Current app version
  lib/
    umqttsimple.py - MQTT library
deploy.bat         - Deploy to ESP32
console.bat        - Open serial console
erase_esp32.bat    - Remove all files from ESP32
```

## Version Management (Optional OTA Feature)

App version is stored in `src/version.json`. To release an update:

1. Update version number in `src/version.json`
2. Commit and push to your UPDATE_URL (GitHub by default)
3. ESP32 will automatically detect the version change within 10 minutes and download updates

**With GitHub (Default):**
```json
// src/version.json
{
  "version": "1.0.1"
}
```
Just push to GitHub and ESP32 will auto-detect within 10 minutes.

**With Custom Hosting:**
1. Host the files at your UPDATE_URL
2. Update `version.json` at `UPDATE_URL/version.json`
3. Host application files at `UPDATE_URL/main.py`, `UPDATE_URL/ble.py`, etc.
4. ESP32 will check and download automatically

**Manual Control:**
You can also manually trigger checks or change behavior via MQTT anytime.
```json
Topic: esp32/ota
{"enabled": false}   // Pause auto-checks
{"url": "http://new-server/src"}  // Switch servers
```