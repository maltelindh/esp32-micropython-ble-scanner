import bluetooth

# Debug flag - set to True to enable logging for each BLE packet
DEBUG = False

scan_queue = {}

def format_addr(addr_bytes):
    return ":".join("{:02X}".format(b) for b in addr_bytes)

def parse_fields(adv):
    i = 0
    n = len(adv)

    while i < n:
        field_len = adv[i]
        if field_len == 0:
            break
        if i + 1 + field_len > n:
            break

        field_type = adv[i + 1]
        field_value = bytes(adv[i + 2 : i + 1 + field_len])

        yield field_type, field_value
        i += 1 + field_len

def extract_16bit_uuids(adv):
    uuids = set()

    for field_type, field_value in parse_fields(adv):
        # 0x02 = Incomplete List of 16-bit Service Class UUIDs
        # 0x03 = Complete List of 16-bit Service Class UUIDs
        # 0x16 = Service Data - 16-bit UUID (first 2 bytes are UUID)
        if field_type == 0x02 or field_type == 0x03:
            for i in range(0, len(field_value) - 1, 2):
                # BLE UUID bytes are little-endian in advertising data
                uuid16 = "{:02X}{:02X}".format(field_value[i + 1], field_value[i])
                uuids.add(uuid16)

        elif field_type == 0x16 and len(field_value) >= 2:
            uuid16 = "{:02X}{:02X}".format(field_value[1], field_value[0])
            uuids.add(uuid16)

    return uuids


def bt_irq(event, data):
    """BLE scan callback"""
    if event == 5: # _IRQ_SCAN_RESULT
        addr_type, addr, adv_type, rssi, adv_data = data

        adv_bytes = bytes(adv_data)
        found_uuids = extract_16bit_uuids(adv_bytes)
        
        if found_uuids:
            mac = format_addr(addr)
            # Store device in queue, overwriting if exists
            scan_queue[mac] = {
                "mac": mac,
                "uuids": list(found_uuids),
                "rssi": rssi,
            }
            if DEBUG:
                print("[BLE] MAC: {} | UUIDs: {} | RSSI: {}".format(
                    mac, found_uuids, rssi
                ))


def start_scan():
    """Start BLE scanning"""
    print("Starting BLE scan...")
    ble = bluetooth.BLE()
    ble.active(True)
    ble.irq(bt_irq)
    ble.gap_scan(0, 30000, 30000, True)
