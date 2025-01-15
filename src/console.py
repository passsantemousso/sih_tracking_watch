messages = {
    "AP00": "IWAP00861265062672529#",
    "AP01": "IWAP01250115V0000.0000N00000.0000E000.1111707323.8708000005200008,612,5,2092,1138945,a|9c-63-5b-c1-16-aa|100&a|76-83-c2-e4-90-07|91&a|44-a3-c7-07-10-1c|75&a|0e-01-4b-1b-4b-3a|73#",
    "AP16": "",
    "AP02": "IWAP02,zh_cn,0,1,612,5,2091|1132805|34,4,a|9c-63-5b-c1-16-aa|110&a|76-83-c2-e4-90-07|88&a|60-bd-2c-b3-bd-29|76&a|62-bd-2c-c3-bd-29|75#",
    "AP03": "IWAP03,08000007000001,00022,00#",
    "AP49": "IWAP49,68#",
    "APHT": "IWAPHT,60,130,85#",
    "APHP": "IWAPHP,83,117,79,98,0.0,36.7#",
    "AP50": "IWAP50,36.7,90#",
    "AP97": "IWAP97,2300@0800,109,001222222113...#"
}


def extract_ap01_data(message: str) -> dict:
    """
    Extrait les données du paquet AP01 et les retourne sous forme de dictionnaire.
    """
    try:
        # Supprimer le préfixe "IWAP01" et le délimiteur final "#"
        content = message[6:-1]
        parts = content.split(",")

        # Extraire les données GPS
        gps_data = parts[0]
        gps_info = {
            "latitude": gps_data[7:16].strip() or None,
            "latitude_direction": gps_data[16].strip() or None,
            "longitude": gps_data[17:27].strip() or None,
            "longitude_direction": gps_data[27].strip() or None,
            "speed": gps_data[28:33].strip() or None,
            "gmt_time": gps_data[33:39].strip() or None,
            "direction_angle": gps_data[39:45].strip() or None,
        }

        # Extraire les informations de statut
        status_raw = parts[1]
        status_info = {
            "gsm_signal": int(status_raw[0:3]) if status_raw[0:3].isdigit() else None,
            "satellites": int(status_raw[3:6]) if status_raw[3:6].isdigit() else None,
            "battery_level": int(status_raw[6:9]) if status_raw[6:9].isdigit() else None,
            "remaining_space": int(status_raw[9:10]) if status_raw[9:10].isdigit() else None,
            "fortification_state": int(status_raw[10:12]) if status_raw[10:12].isdigit() else None,
            "working_mode": int(status_raw[12:14]) if status_raw[12:14].isdigit() else None,
        }

        # Extraire les informations Bluetooth
        bluetooth_raw = parts[2].split("&")
        bluetooth_info = []
        for bt in bluetooth_raw:
            bt_parts = bt.split("|")
            if len(bt_parts) == 3:
                bluetooth_info.append({
                    "name": bt_parts[0].strip() or None,
                    "mac": bt_parts[1].strip() or None,
                    "signal_strength": int(bt_parts[2]) if bt_parts[2].isdigit() else None,
                })

        # Extraire les données LBS
        lbs_raw = parts[3:5]
        lbs_info = []
        for lbs in lbs_raw:
            lbs_parts = lbs.split("|")
            if len(lbs_parts) == 4:
                lbs_info.append({
                    "mcc": int(lbs_parts[0]) if lbs_parts[0].isdigit() else None,
                    "mnc": int(lbs_parts[1]) if lbs_parts[1].isdigit() else None,
                    "lac": int(lbs_parts[2]) if lbs_parts[2].isdigit() else None,
                    "cid": int(lbs_parts[3]) if lbs_parts[3].isdigit() else None,
                })

        # Extraire les informations WiFi
        wifi_raw = parts[5:]
        wifi_info = []
        for wifi in wifi_raw:
            wifi_parts = wifi.split("|")
            if len(wifi_parts) == 3:
                wifi_info.append({
                    "ssid": wifi_parts[0].strip() or None,
                    "mac": wifi_parts[1].strip() or None,
                    "signal_strength": int(wifi_parts[2]) if wifi_parts[2].isdigit() else None,
                })

        # Retourner les informations extraites sous forme de dictionnaire
        return {
            "gps": gps_info,
            "status": status_info,
            "bluetooth": bluetooth_info,
            "lbs": lbs_info,
            "wifi": wifi_info,
        }
    except Exception as e:
        print(f"Erreur lors de l'extraction des données AP01 : {e}")
        return {}



if __name__ == "__main__":
    data = extract_ap01_data(messages['AP01'])
    print(data)