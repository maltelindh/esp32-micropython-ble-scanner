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

def extract_uuids(adv):
    uuids = set()

    for field_type, field_value in parse_fields(adv):
        # 16-bit UUIDs
        # 0x02 = Incomplete List of 16-bit Service Class UUIDs
        # 0x03 = Complete List of 16-bit Service Class UUIDs
        # 0x16 = Service Data - 16-bit UUID (first 2 bytes are UUID)
        if field_type == 0x02 or field_type == 0x03:
            for i in range(0, len(field_value) - 1, 2):
                uuid16 = "{:02X}{:02X}".format(field_value[i + 1], field_value[i])
                uuids.add(uuid16)

        elif field_type == 0x16 and len(field_value) >= 2:
            uuid16 = "{:02X}{:02X}".format(field_value[1], field_value[0])
            uuids.add(uuid16)

        # 32-bit UUIDs
        # 0x04 = Incomplete List of 32-bit Service Class UUIDs
        # 0x05 = Complete List of 32-bit Service Class UUIDs
        # 0x20 = Service Data - 32-bit UUID
        elif field_type == 0x04 or field_type == 0x05:
            for i in range(0, len(field_value) - 3, 4):
                uuid32 = "{:02X}{:02X}{:02X}{:02X}".format(
                    field_value[i + 3], field_value[i + 2], field_value[i + 1], field_value[i]
                )
                uuids.add(uuid32)

        elif field_type == 0x20 and len(field_value) >= 4:
            uuid32 = "{:02X}{:02X}{:02X}{:02X}".format(
                field_value[3], field_value[2], field_value[1], field_value[0]
            )
            uuids.add(uuid32)

        # 128-bit UUIDs
        # 0x06 = Incomplete List of 128-bit Service Class UUIDs
        # 0x07 = Complete List of 128-bit Service Class UUIDs
        # 0x21 = Service Data - 128-bit UUID
        elif field_type == 0x06 or field_type == 0x07:
            for i in range(0, len(field_value) - 15, 16):
                uuid128 = "".join("{:02X}".format(field_value[i + 15 - j]) for j in range(16))
                uuids.add(uuid128)

        elif field_type == 0x21 and len(field_value) >= 16:
            uuid128 = "".join("{:02X}".format(field_value[15 - j]) for j in range(16))
            uuids.add(uuid128)

    return uuids


def bt_irq(event, data):
    """BLE scan callback"""
    if event == 5: # _IRQ_SCAN_RESULT
        addr_type, addr, adv_type, rssi, adv_data = data
        
        # Filter by advertisement type early to avoid processing unwanted types
        # 0 = ADV_IND, 1 = ADV_DIRECT_IND 2 = ADV_SCAN_IND, 3 = ADV_NONCONN_IND, 4 = SCAN_RSP
        if adv_type != 3 and not DEBUG:
            return

        adv_bytes = bytes(adv_data)
        found_uuids = extract_uuids(adv_bytes)
        
        if found_uuids:
            mac = format_addr(addr)
            # Store device in queue, overwriting if exists
            scan_queue[mac] = {
                "mac": mac,
                "uuids": list(found_uuids),
                "rssi": rssi,
            }
            if DEBUG:
                print("[BLE] MAC: {} | UUIDs: {} | RSSI: {} | TYPE: {}".format(
                    mac, found_uuids, rssi, adv_type
                ))


def start_scan():
    """Start BLE scanning"""
    print("Starting BLE scan...")
    ble = bluetooth.BLE()
    ble.active(True)
    ble.irq(bt_irq)
    ble.gap_scan(0, 300000, 30000, False)
