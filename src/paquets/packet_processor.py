import datetime
from datetime import timezone


class PacketProcessor:
    """Classe pour gérer le traitement des différents paquets."""

    @staticmethod
    def extract_ap00_data(message: str) -> dict:
        """Extrait les données du paquet AP00 (Login) et retourne l'IMEI."""
        try:
            imei = message[6:-1]  # Extraction de l'IMEI
            return {"imei": imei}
        except Exception as e:
            print(f"Erreur lors de l'extraction des données AP00 : {e}")
            return {}

    @staticmethod
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

    @staticmethod
    def extract_ap02_data(message: str) -> dict:
        """
        Extrait les données du paquet AP02 et les retourne sous forme de dictionnaire.

        Args:
            message (str): Le message reçu pour la commande AP02.

        Returns:
            dict: Un dictionnaire contenant les informations extraites.
        """
        try:
            # Supprimer le préfixe "IWAP02," et le délimiteur final "#"
            content = message[7:-1]
            parts = content.split(',')

            # Extraire la langue
            language = parts[0].split('|')[0]

            # Extraire les informations Bluetooth
            bluetooth_info = []
            if '@' in parts[0]:
                bt_raw = parts[0].split('|')[1:]
                for bt in bt_raw:
                    if '@' in bt:
                        _, bt_data = bt.split('@', 1)
                    else:
                        bt_data = bt
                    bt_parts = bt_data.split('&')
                    for b in bt_parts:
                        bt_detail = b.split('|')
                        if len(bt_detail) == 3:
                            bluetooth_info.append({
                                "name": bt_detail[0],
                                "mac": bt_detail[1],
                                "signal_strength": int(bt_detail[2])
                            })

            # Extraire le MCC, le MNC et le nombre de bases
            mcc = parts[3]
            mnc = parts[4]
            base_count = int(parts[2])
            bases_info = []
            base_raw = parts[5:5 + base_count]
            for base in base_raw:
                base_parts = base.split('|')
                if len(base_parts) == 3:
                    bases_info.append({
                        "lac": int(base_parts[0]),
                        "cid": int(base_parts[1]),
                        "signal_strength": 150 - abs(int(base_parts[2]))
                    })

            # Extraire les informations WiFi
            wifi_info = []
            wifi_count = int(parts[5 + base_count])
            wifi_raw = parts[6 + base_count:]
            for wifi in wifi_raw:
                wifi_parts = wifi.split('|')
                if len(wifi_parts) == 3:
                    wifi_info.append({
                        "ssid": wifi_parts[0],
                        "mac": wifi_parts[1],
                        "signal_strength": 150 - abs(int(wifi_parts[2]))
                    })

            # Retourner les informations extraites sous forme de dictionnaire
            return {
                "language": language,
                "bluetooth": bluetooth_info,
                "mcc": mcc,
                "mnc": mnc,
                "bases": bases_info,
                "wifi": wifi_info
            }

        except Exception as e:
            print(f"Erreur lors de l'extraction des données AP02 : {e}")
            return {}

    @staticmethod
    def extract_ap03_data(message: str) -> dict:
        """Extrait les données du message AP03 et les structure sous forme de dictionnaire."""
        data = {}

        try:
            # Suppression du préfixe IWAP03 et du suffixe #
            message = message[7:-1]

            # Découpage du message en parties
            parts = message.split(',')

            # Extraction des informations
            gsm_signal = parts[0][:3]  # GSM signal (non utilisé)
            num_satellites = parts[0][3:6]  # Nombre de satellites
            battery_level = parts[0][6:8]  # Niveau de batterie
            remaining_space = parts[0][8:9]  # Espace restant
            fortification_state = parts[0][9:11]  # État de fortification (2 hexadécimaux)
            working_mode = parts[0][11:13]  # Mode de travail

            steps_count = parts[1]  # Nombre de pas comptés
            rolls_frequency = parts[2]  # Fréquence des rouleaux

            # Structure des données extraites
            data['gsm_signal'] = gsm_signal
            data['num_satellites'] = num_satellites
            data['battery_level'] = battery_level
            data['remaining_space'] = remaining_space
            data['fortification_state'] = fortification_state
            data['working_mode'] = working_mode
            data['steps_count'] = steps_count
            data['rolls_frequency'] = rolls_frequency

        except Exception as e:
            print(f"Erreur lors de l'extraction des données AP03 : {e}")
            return {}

        return data

    @staticmethod
    def extract_ap16_data(message: str) -> dict:
        """Extrait les données du paquet AP16 (localisation en temps réel)."""
        try:
            parts = message[6:-1].split(",")
            journal_no = parts[0]
            return {"journal_no": journal_no}
        except Exception as e:
            print(f"Erreur lors de l'extraction des données AP16 : {e}")
            return {}

    @staticmethod
    def extract_ap49_data(message: str) -> dict:
        """
        Extrait les données du message AP49 (Upload heart rate) et les structure sous forme de dictionnaire.

        Le message contient uniquement le rythme cardiaque après le préfixe "IWAP49,".
        Exemple de message : IWAP49,68#

        Args:
            message (str): Le message reçu pour la commande AP49.

        Returns:
            dict: Un dictionnaire contenant le rythme cardiaque extrait.
        """
        data = {}

        try:
            # Suppression du préfixe IWAP49 et du suffixe #
            message = message[6:-1]

            # Extraction du rythme cardiaque
            heart_rate = message.strip()

            # Structure des données extraites
            data['heart_rate'] = heart_rate

        except Exception as e:
            print(f"Erreur lors de l'extraction des données AP49 : {e}")
            return {}

        return data


    @staticmethod
    def extract_ap50_data(message: str) -> dict:
        """
        Extrait les données du message AP50 (Upload body temperature) et les structure sous forme de dictionnaire.

        Le message contient la température corporelle et le niveau de la batterie. Les valeurs manquantes sont laissées vides.
        Exemple de message : IWAP50,36.7,90#

        Args:
            message (str): Le message reçu pour la commande AP50.

        Returns:
            dict: Un dictionnaire contenant les données extraites : température corporelle et niveau de batterie.
        """
        data = {}

        try:
            # Suppression du préfixe IWAP50 et du suffixe #
            message = message[6:-1]

            # Découpage du message en valeurs
            values = message.split(',')

            # Extraction des valeurs (avec vérification des valeurs manquantes)
            data['body_temperature'] = values[0] if values[0] else None
            data['battery_level'] = values[1] if values[1] else None

        except Exception as e:
            print(f"Erreur lors de l'extraction des données AP50 : {e}")
            return {}

        return data


    @staticmethod
    def extract_ap97_data(message: str) -> dict:
        """
        Extrait les données du message AP97 (Sleep data) et les structure sous forme de dictionnaire.

        Le message contient la période statistique, le nombre total de données et le statut du sommeil.
        Exemple de message : IWAP97,2300@0800,109,001222222113#

        Args:
            message (str): Le message reçu pour la commande AP97.

        Returns:
            dict: Un dictionnaire contenant les données extraites : période statistique, nombre total de données, et statut du sommeil.
        """
        data = {}

        try:
            # Suppression du préfixe IWAP97 et du suffixe #
            message = message[6:-1]

            # Découpage du message en valeurs
            values = message.split(',')

            # Extraction des valeurs
            data['statistical_period'] = values[0] if values[0] else None
            data['total_data_count'] = int(values[1]) if values[1].isdigit() else None
            data['sleep_status'] = values[2] if values[2] else None

        except Exception as e:
            print(f"Erreur lors de l'extraction des données AP97 : {e}")
            return {}

        return data


    @staticmethod
    def extract_apht_data(message: str) -> dict:
        """
        Extrait les données du message APHT (Upload heart rate and BP) et les structure sous forme de dictionnaire.

        Le message contient le rythme cardiaque, la pression systolique et la pression diastolique séparés par des virgules.
        Exemple de message : IWAPHT,60,130,85#

        Args:
            message (str): Le message reçu pour la commande APHT.

        Returns:
            dict: Un dictionnaire contenant les données extraites : rythme cardiaque, pression systolique et pression diastolique.
        """
        data = {}

        try:
            # Suppression du préfixe IWAPHT et du suffixe #
            message_content = message[7:-1]

            # Découpage du message en valeurs
            values = message_content.split(',')

            # Vérification du nombre de valeurs et extraction sécurisée
            if len(values) >= 3:
                data['heart_rate'] = values[0]
                data['systolic_pressure'] = values[1]
                data['diastolic_pressure'] = values[2]
            else:
                print(f"Message APHT invalide ou incomplet : {message}")

        except Exception as e:
            print(f"Erreur lors de l'extraction des données APHT : {e}")
            return {}

        return data


    @staticmethod
    def extract_aphp_data(message: str) -> dict:
        """
        Extrait les données du message APHP (Upload heart rate, BP, SPO2, blood sugar) et les structure sous forme de dictionnaire.

        Le message contient les valeurs du rythme cardiaque, de la pression artérielle, de la saturation en oxygène,
        de la glycémie et de la température séparées par des virgules. Les valeurs manquantes sont laissées vides.
        Exemple de message : IWAPHP,60,130,85,95,90,36.5,,,,,,,#

        Args:
            message (str): Le message reçu pour la commande APHP.

        Returns:
            dict: Un dictionnaire contenant les données extraites : rythme cardiaque, pression systolique, pression diastolique,
                  SPO2, glycémie et température.
        """
        data = {}

        try:
            # Suppression du préfixe IWAPHP et du suffixe #
            message = message[7:-1]

            # Découpage du message en valeurs
            values = message.split(',')

            # Extraction des valeurs (avec vérification des valeurs manquantes)
            data['heart_rate'] = values[0] if values[0] else None
            data['systolic_pressure'] = values[1] if values[1] else None
            data['diastolic_pressure'] = values[2] if values[2] else None
            data['spo2'] = values[3] if values[3] else None
            data['blood_sugar'] = values[4] if values[4] else None
            data['temperature'] = values[5] if values[5] else None

        except Exception as e:
            print(f"Erreur lors de l'extraction des données APHP : {e}")
            return {}

        return data

    def process_message(self, message: str) -> str | None:
        """Traite les messages reçus et génère une réponse appropriée."""
        try:
            if message.startswith("IWAP00"):
                # Traitement pour AP00 Login package
                data = self.extract_ap00_data(message)
                print(f"Données extraites pour AP00 : {data}")
                server_time = datetime.datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
                return f"IWBP00,{server_time},8#"

            elif message.startswith("IWAP01"):
                # Traitement pour AP01 Locating package
                data = self.extract_ap01_data(message)
                print(f"Données extraites pour AP01 : {data}")
                return "IWBP01#"

            elif message.startswith("IWAP02"):
                # Traitement pour AP02 Multiple bases locating package
                data = self.extract_ap02_data(message)
                print(f"Données extraites pour AP02 : {data}")
                return "IWBP02#"

            elif message.startswith("IWAP03"):
                # Traitement pour AP03 Heartbeat package
                data = self.extract_ap03_data(message)
                print(f"Données extraites pour AP03 : {data}")
                return "IWBP03#"

            elif message.startswith("IWAP16"):
                # Traitement pour AP16 Real-time location
                data = self.extract_ap16_data(message)
                print(f"Données extraites pour AP16 : {data}")
                return "IWBP16#"

            elif message.startswith("IWAP49"):
                # Traitement pour AP49 Upload heart rate
                data = self.extract_ap49_data(message)
                print(f"Données extraites pour AP49 : {data}")
                return "IWBP49#"

            elif message.startswith("IWAP50"):
                # Traitement pour AP50 Upload body temperature
                data = self.extract_ap50_data(message)
                print(f"Données extraites pour AP50 : {data}")
                return "IWBP50#"

            elif message.startswith("IWAP97"):
                # Traitement pour AP97 Sleep data
                data = self.extract_ap97_data(message)
                print(f"Données extraites pour AP97 : {data}")
                return "IWBP97#"

            elif message.startswith("IWAPHT"):
                # Traitement pour APHT Upload heart rate and BP
                data = self.extract_apht_data(message)
                print(f"Données extraites pour APHT : {data}")
                return "IWBPHT#"

            elif message.startswith("IWAPHP"):
                # Traitement pour APHP Upload heart rate, BP, SPO2, blood sugar
                data = self.extract_aphp_data(message)
                print(f"Données extraites pour APHP : {data}")
                return "IWBPHP#"

            else:
                print(f"Paquet non reconnu : {message}")
                return None
        except Exception as e:
            print(f"Erreur lors du traitement du message : {e}")
            return None

    @staticmethod
    def process_message_response(message: str) -> str | None:
        """Génère une réponse appropriée pour chaque cas."""
        try:
            if message.startswith("IWAP00"):
                server_time = datetime.datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
                return f"IWBP00,{server_time},8#"

            elif message.startswith("IWAP01"):
                return "IWBP01#"

            elif message.startswith("IWAP02"):
                return "IWBP02#"

            elif message.startswith("IWAP03"):
                return "IWBP03#"

            elif message.startswith("IWAP16"):
                return "IWBP16#"

            elif message.startswith("IWAP49"):
                return "IWBP49#"

            elif message.startswith("IWAP50"):
                return "IWBP50#"

            elif message.startswith("IWAP97"):
                return "IWBP97#"

            elif message.startswith("IWAPHT"):
                return "IWBPHT#"

            elif message.startswith("IWAPHP"):
                return "IWBPHP#"

            else:
                print(f"Paquet non reconnu : {message}")
                return None
        except Exception as e:
            print(f"Erreur lors du traitement du message : {e}")
            return None
