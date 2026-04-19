import time
import ble
import mqtt
import updater

try:
    from secrets import UPDATE_URL
except (ImportError, AttributeError):
    UPDATE_URL = None

last_mqtt_send = 0
last_mqtt_ping = 0
last_update_check = 0

# Config - tweak as you like
MQTT_TOPIC_BLE_SCAN = "esp32/ble/scan"
MQTT_TOPIC_OTA = "esp32/ota"
MQTT_BATCH_SIZE = 20
MQTT_INTERVAL = 5000  # 5s
MQTT_PING_INTERVAL = 30000  # 30s
OTA_CHECK_INTERVAL = 600000  # 10 minutes

def ticks():
    return time.ticks_ms()

# Initialize
mqtt_client = mqtt.initialize()

# Register OTA control callback
mqtt.register_callback(MQTT_TOPIC_OTA, updater.on_update_message)
ota_status = "enabled (auto-check every 10 min)" if (UPDATE_URL and len(UPDATE_URL) > 0) else "disabled"
print("OTA: {}".format(ota_status))

ble.start_scan()

while True:
    now = ticks()
    
    # Check for incoming messages
    mqtt.check_messages()
    
    # Send MQTT results periodically
    if time.ticks_diff(now, last_mqtt_send) >= MQTT_INTERVAL:
        last_mqtt_send = now
        mqtt.send_mqtt_batch()
    
    # Keep MQTT connection alive
    if time.ticks_diff(now, last_mqtt_ping) >= MQTT_PING_INTERVAL:
        last_mqtt_ping = now
        mqtt.ping_broker()
    
    # Check for OTA updates periodically (every 10 minutes)
    if time.ticks_diff(now, last_update_check) >= OTA_CHECK_INTERVAL:
        last_update_check = now
        updater.check_for_updates()
    
    time.sleep_ms(200)