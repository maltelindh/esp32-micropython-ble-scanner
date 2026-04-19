import machine
import network
import time
import os
import sys
from secrets import WIFI_SSID, WIFI_PASSWORD

def connect_wifi(timeout_ms=15000):
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)

    if wlan.isconnected():
        print("Already connected:", wlan.ipconfig("addr4"))
        return

    wlan.config(reconnects=3)

    print("Connecting to Wi-Fi...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    start = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            led.value(1)
            raise RuntimeError("Wi-Fi connection timeout")
        machine.idle()
        time.sleep_ms(100)

    print("Connected:", wlan.ipconfig("addr4"))

def updateFiles():
    files = os.listdir()
    for file in files:
        # Never replace boot.py (this file)
        if file.startswith("boot.py"):
            continue
        if file.endswith(".py_new"):
            existing_file = file[:-4]  # Remove "_new" suffix
            print("Updating file:", existing_file)
            if existing_file in files:
                os.remove(existing_file)
            os.rename(file, existing_file)


# Turns LED on during boot, turns off after Wi-Fi is connected
led = machine.Pin(2, machine.Pin.OUT)
led.value(1)

try:
    connect_wifi()
    led.value(0)
except Exception as e:
    print("Wi-Fi failed:", e)

try:
    updateFiles()
except Exception as e:
    print("File update failed:", e)