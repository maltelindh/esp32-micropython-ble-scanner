import time
import network
import json
from lib.umqttsimple import MQTTClient
from secrets import MQTT_BROKER, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
from ble import scan_queue

mqtt_client = None
esp_ip = None

# Topic -> callback handler mapping
topic_handlers = {}


def get_local_ip():
    """Get ESP32 local IP address"""
    wlan = network.WLAN(network.WLAN.IF_STA)
    if not wlan.isconnected():
        raise RuntimeError("No Wi-Fi connection, cannot get local IP")
    return wlan.ifconfig()[0]


def message_dispatcher(topic, msg):
    """Dispatch incoming messages to registered topic handlers"""
    if topic in topic_handlers:
        try:
            topic_handlers[topic](topic, msg)
        except Exception as e:
            print("Error in topic handler for {}: {}".format(topic, e))
    else:
        print("No handler registered for topic:", topic)


def connect_mqtt():
    """Connect to MQTT broker"""
    global mqtt_client, esp_ip
    try:
        client_id = esp_ip
        mqtt_client = MQTTClient(client_id, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
        mqtt_client.set_callback(message_dispatcher)
        mqtt_client.connect()
        print("Connected to MQTT broker:", MQTT_BROKER)
        return mqtt_client
    except OSError as e:
        print("MQTT connection failed:", e)
        mqtt_client = None
        return None


def restart_and_reconnect():
    """Wait and retry MQTT connection"""
    print("Reconnecting after 10 seconds...")
    time.sleep(10)
    connect_mqtt()


def send_mqtt_batch():
    """Send pending scan results in batches of max 20"""
    global mqtt_client, esp_ip
    from main import MQTT_TOPIC_BLE_SCAN, MQTT_BATCH_SIZE
    
    if not mqtt_client:
        return
    
    # Get all devices in queue
    devices = list(scan_queue.values())
    
    if not devices:
        return
    
    for i in range(0, len(devices), MQTT_BATCH_SIZE):
        batch = devices[i:i + MQTT_BATCH_SIZE]
        
        try:
            payload = json.dumps({"ip": esp_ip, "devices": batch})
            mqtt_client.publish(MQTT_TOPIC_BLE_SCAN, payload, qos=0)
            print("Sent {} devices to MQTT".format(len(batch)))
            
            # Remove sent devices from queue
            for dev in batch:
                del scan_queue[dev["mac"]]
                
        except OSError as e:
            print("MQTT publish failed:", e)
            restart_and_reconnect()


def ping_broker():
    """Send ping to keep MQTT connection alive"""
    global mqtt_client
    
    try:
        if mqtt_client:
            mqtt_client.ping()
    except OSError as e:
        print("MQTT ping failed:", e)
        restart_and_reconnect()


def check_messages():
    """Check for incoming MQTT messages"""
    global mqtt_client
    
    try:
        if mqtt_client:
            mqtt_client.check_msg()
    except OSError as e:
        print("MQTT check_msg failed:", e)
        restart_and_reconnect()


def register_callback(topic, callback):
    """Register a callback handler for a specific topic"""
    global mqtt_client
    
    topic_bytes = topic if isinstance(topic, bytes) else topic.encode()
    topic_handlers[topic_bytes] = callback
    
    if mqtt_client:
        try:
            mqtt_client.subscribe(topic_bytes)
            print("Subscribed to {} with handler".format(topic))
        except Exception as e:
            print("Failed to subscribe to {}: {}".format(topic, e))
    else:
        print("MQTT client not connected, cannot subscribe to {}".format(topic))


def initialize():
    """Initialize MQTT connection"""
    global esp_ip
    esp_ip = get_local_ip()
    return connect_mqtt()
