import machine
import json
import urequests
import time

try:
    from secrets import UPDATE_URL
except (ImportError, AttributeError):
    UPDATE_URL = None

# Should NOT be updated via OTA
PROTECTED_FILES = {"boot.py"}

# Files to update via OTA (includes files in subdirs)
UPDATABLE_FILES = {
    "main.py", 
    "ble.py", 
    "mqtt.py", 
    "updater.py", 
    "secrets.py", 
    "version.json",
    # Libraries
    "lib/umqttsimple.py"
}

update_in_progress = False
ota_enabled = bool(UPDATE_URL and len(UPDATE_URL) > 0)
update_url = UPDATE_URL


def get_local_version():
    """Read local version from version.json"""
    try:
        with open("version.json", "r") as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    except Exception as e:
        print("Update: Error reading local version:", e)
        return "0.0.0"


def get_remote_version():
    """Fetch version from remote URL"""
    global ota_enabled, update_url
    
    if not ota_enabled or not update_url:
        return None
    
    try:
        url = "{}/version.json".format(update_url.rstrip("/"))
        print("Update: Fetching version from {}...".format(url))
        response = urequests.get(url, timeout=10)
        
        if response.status_code != 200:
            print("Update: Failed to fetch version: HTTP {}".format(response.status_code))
            response.close()
            return None
        
        data = json.loads(response.text)
        response.close()
        
        version = data.get("version")
        return version
        
    except Exception as e:
        print("Update: Error fetching remote version:", e)
        return None


def check_for_updates():
    """Periodically check for updates"""
    global last_version_check, ota_enabled, update_in_progress, update_url
    
    # Skip if already checking, OTA disabled, or no URL configured
    if update_in_progress or not ota_enabled or not update_url:
        return
    
    local_version = get_local_version()
    remote_version = get_remote_version()
    
    if not remote_version:
        return
    
    print("Update: Local={}, Remote={}".format(local_version, remote_version))
    
    if local_version != remote_version:
        print("Update: Version mismatch detected, starting download...")
        download_and_update()


def download_and_update():
    """Download files and trigger reboot"""
    global update_in_progress, ota_enabled, update_url
    
    if not ota_enabled or not update_url:
        return
    
    update_in_progress = True
    
    downloaded_count = 0
    for filename in UPDATABLE_FILES:
        if filename in PROTECTED_FILES:
            print("Update: Skipping protected file:", filename)
            continue
        
        if download_file(filename):
            downloaded_count += 1
    
    if downloaded_count > 0:
        print("Update: Downloaded {} files, rebooting...".format(downloaded_count))
        time.sleep(1)
        machine.reset()
    else:
        print("Update: No files downloaded")
        update_in_progress = False


def on_update_message(topic, msg):
    """Handle MQTT OTA control messages"""
    global ota_enabled, update_url
    
    try:
        payload = json.loads(msg.decode("utf-8"))
        
        # Handle URL update
        if "url" in payload:
            new_url = payload["url"]
            if new_url and len(new_url) > 0:
                update_url = new_url
                ota_enabled = True
                print("Update: URL changed to {}".format(new_url))
            else:
                update_url = None
                ota_enabled = False
                print("Update: OTA disabled (empty URL)")
        
        # Handle enable/disable
        if "enabled" in payload:
            ota_enabled = bool(payload["enabled"]) and bool(update_url and len(update_url) > 0)
            print("Update: OTA {}".format("enabled" if ota_enabled else "disabled"))
        
    except Exception as e:
        print("Update: Error processing message:", e)


def download_file(filename):
    """Download a file from UPDATE_URL"""
    global update_url
    
    try:
        url = "{}/{}".format(update_url.rstrip("/"), filename)
        print("Update: Downloading {}...".format(filename))
        
        response = urequests.get(url, timeout=10)
        
        if response.status_code != 200:
            print("Update: Failed to download {}: HTTP {}".format(filename, response.status_code))
            response.close()
            return False
        
        # Create dir if path
        if "/" in filename:
            import os
            dir_path = filename.rsplit("/", 1)[0]
            try:
                os.mkdir(dir_path)
            except OSError:
                pass  # dir exists
        
        # Save with suffix
        new_filename = "{}_new".format(filename)
        
        with open(new_filename, "wb") as f:
            f.write(response.content)
        
        response.close()
        print("Update: Saved {}".format(new_filename))
        return True
        
    except Exception as e:
        print("Update: Error downloading {}: {}".format(filename, e))
        return False
