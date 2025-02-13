from datetime import datetime, timezone


class WatchCommandService:
    """
    Service pour générer les commandes serveur => montre (BPxx).
    Chaque méthode construit la chaîne de caractères
    (par exemple : IWBP12,IMEI,xxx,...) selon la notice du protocole.
    """

    def __init__(self):
        pass

    @staticmethod
    def to_unicode_hex(text: str) -> str:
        """
        Convertit un texte en une chaîne unicode hex format
        """
        return "".join(f"{ord(c):04x}" for c in text)

    @staticmethod
    def generate_journal_no_datetime() -> str:
        return datetime.now().strftime("%Y%m%d%H%M%S")


    def set_sos_numbers(self, imei: str, sos1: str, sos2: str, sos3: str) -> str:
        """
        BP12 : Définir les numéros SOS (jusqu'à 3).

        Exemple : IWBP12,353456789012345,080835,135XXXXXXXX,135XXXXXXXX,135XXXXXXXX#
        """
        return f"IWBP12,{imei},{self.generate_journal_no_datetime()},{sos1},{sos2},{sos3}#"


    def set_whitelist(self, imei: str, contacts: list) -> str:
        """
        BP14 : Définir la liste blanche/contacts de la montre (jusqu'à 10 numéros).
        Chaque contact est codé en UNICODE, ex : D3590D54|135xxxxxxxxxx
        Les contacts sont séparés par des virgules.

        Exemple:
          IWBP14,353456789012345,080835,D3590D54|135xxxxxxxxxx, D3590D54|135xxxxxxxxxx,...
        """
        # Concatène tous les contacts en les séparant par des virgules
        contact_str = ",".join(contacts)
        return f"IWBP14,{imei},{self.generate_journal_no_datetime()},{contact_str}#"


    def real_time_locating(self, imei: str) -> str:
        """
        BP16 : Commande de localisation en temps réel.

        Exemple : IWBP16,353456789012345,080835#
        """
        return f"IWBP16,{imei},{self.generate_journal_no_datetime()}#"


    def factory_reset(self, imei: str) -> str:
        """
        BP17 : Réinitialisation aux paramètres d'usine.

        Exemple : IWBP17,353456789012345,080835#
        """
        return f"IWBP17,{imei},{self.generate_journal_no_datetime()}#"


    def restart_device(self, imei: str) -> str:
        """
        BP18 : Redémarrer l'appareil (montre).

        Exemple : IWBP18,353456789012345,080835#
        """
        return f"IWBP18,{imei},{self.generate_journal_no_datetime()}#"


    def set_timezone(self, imei: str, language_flag: str) -> str:
        """
        BP20 : Définir le fuseau horaire.

        Exemple : IWBP20,353456789012345,080835,0,8#
        - 0 : language (non utilisé)
        - 8 : fuseau horaire (peut être négatif ou positif)
        """
        return f"IWBP20,{imei},{self.generate_journal_no_datetime()},{language_flag},{timezone}#"


    @staticmethod
    def send_audio_message(sender_name: str, extra_data: str, total_packets: int, sequence: int, packet_size: int,
                           audio_data: str) -> str:
        """
        BP28 : Envoyer un message audio à la montre.
        - sender_name : nom de l'expéditeur encodé en UNICODE (ex. D3590D54)
        - extra_data : champ supplémentaire
        - total_packets : nombre total de packets audio
        - sequence : numéro de séquence de ce packet
        - packet_size : taille en octets du bloc audio
        - audio_data : data audio encodée en hex ou base64 selon le protocole

        Exemple : IWBP28, D3590D54,XXXX,6,1,1024,XXXXXXXXXX#
        """
        return f"IWBP28,{sender_name},{extra_data},{total_packets},{sequence},{packet_size},{audio_data}#"


    def power_off(self, imei: str) -> str:
        """
        BP31 : Éteindre la montre à distance.

        Exemple : IWBP31,353456789012345,080835#
        """
        return f"IWBP31,{imei},{self.generate_journal_no_datetime()}#"


    def set_working_mode(self, imei: str, mode: int) -> str:
        """
        BP33 : Définir le mode de fonctionnement.
        1 => normal
        2 => économie d'énergie
        3 => urgence
        Exemple : IWBP33,353456789012345,080835,1#
        """
        return f"IWBP33,{imei},{self.generate_journal_no_datetime()},{mode}#"


    def set_working_mode_free(self, imei: str, mode: int, interval_sec: int, gps_on: int) -> str:
        """
        BP34 : Mode libre (intervalle custom, GPS on/off).

        Exemple : IWBP34,353456789012345,080835,8,30,1#
        - mode=8
        - interval=30 (secondes)
        - gps_on=1
        """
        return f"IWBP34,{imei},{self.generate_journal_no_datetime()},{mode},{interval_sec},{gps_on}#"


    def send_text_message(self, imei: str, text_unicode: str) -> str:
        """
        BP40 : Envoyer un message texte en UNICODE.

        Exemple : IWBP40,353456789012345,080835,00610072006500200079006f00750020006f006b003f#
        """
        return f"IWBP40,{imei},{self.generate_journal_no_datetime()},{self.to_unicode_hex(text_unicode)}#"


    def fall_down_switch(self, imei: str, on_off: int) -> str:
        """
        BP76 : Activer/désactiver la détection de chute.
        on_off : 1 => actif, 0 => inactif

        Exemple : IWBP76,353456789012345,080835,1#
        """
        return f"IWBP76,{imei},{self.generate_journal_no_datetime()},{on_off}#"


    def fall_down_sensitivity(self, imei: str, level: int) -> str:
        """
        BP77 : Sensibilité de la détection de chute.
        level : 1/2/3 => 3 étant le plus sensible

        Exemple : IWBP77,353456789012345,080835,1#
        """
        return f"IWBP77,{imei},{self.generate_journal_no_datetime()},{level}#"


    def switch_white_list(self, imei: str, on_off: int) -> str:
        """
        BP84 : Activer/désactiver le White list.
        on_off : 1 => on, 0 => off

        Exemple : IWBP84,353456789012345,080835,1#
        """
        return f"IWBP84,{imei},{self.generate_journal_no_datetime()},{on_off}#"


    def set_alarm(self, imei: str, master_switch: int, total_alarms: int, alarm_str: str) -> str:
        """
        BP85 : Définir une alarme ou un rappel.
        - master_switch : 1 => toutes les alarmes actives, 0 => inactives
        - total_alarms : nombre total d'alarmes
        - alarm_str : liste des alarmes, ex : '0900,135,1,1@0900,135,1,2@0900,135,1,3'
          (format de la notice : heure, jours, switch, type)

        Exemple : IWBP85,353456789012345,080835,1,3,0900,135,1,1@0900,135,1,2@0900,135,1,3#
        """
        return f"IWBP85,{imei},{self.generate_journal_no_datetime()},{master_switch},{total_alarms},{alarm_str}#"


    def set_heart_rate_interval(self, imei: str, on_off: int, interval_min: int) -> str:
        """
        BP86 : Définir l'intervalle de mesure automatique de la fréquence cardiaque.
        - on_off : 1 => activé, 0 => désactivé
        - interval_min : intervalle en minutes

        Exemple : IWBP86,353456789012345,080835,1,720#
        """
        return f"IWBP86,{imei},{self.generate_journal_no_datetime()},{on_off},{interval_min}#"


    def test_heart_rate(self, imei: str) -> str:
        """
        BPXL : Lancer un test de fréquence cardiaque instantané.

        Exemple : IWBPXL,353456789012345,080835#
        """
        return f"IWBPXL,{imei},{self.generate_journal_no_datetime()}#"


    def test_blood_pressure(self, imei: str) -> str:
        """
        BPXY : Tester la tension artérielle.

        Exemple : IWBPXY,353456789012345,080835#
        """
        return f"IWBPXY,{imei},{self.generate_journal_no_datetime()}#"


    def test_temperature(self, imei: str) -> str:
        """
        BPXT : Tester la température.

        Exemple : IWBPXT,353456789012345,080835#
        """
        return f"IWBPXT,{imei},{self.generate_journal_no_datetime()}#"


    def calibrate_blood_pressure(self, imei: str, sbp: int, dbp: int, age: int, gender: int) -> str:
        """
        BPJZ : Calibration de la pression artérielle.
        - sbp : systolic
        - dbp : diastolic
        - age : âge
        - gender : 1 => homme, 0 => femme

        Exemple : IWBPJZ,353456789012345,080835,110,75,80,1#
        """
        return f"IWBPJZ,{imei},{self.generate_journal_no_datetime()},{sbp},{dbp},{age},{gender}#"


    def set_auto_test_temperature(self, imei: str, on_off: int, interval_min: int) -> str:
        """
        BP87 : Définir la mesure automatique de la température.
        - on_off : 1 => activé, 0 => désactivé
        - interval_min : intervalle en minutes

        Exemple : IWBP87,353456789012345,080835,1,720#
        """
        return f"IWBP87,{imei},{self.generate_journal_no_datetime()},{on_off},{interval_min}#"


    def test_blood_oxygen( self, imei: str) -> str:
        """
        BPXZ : Tester la saturation en oxygène (SPO2).

        Exemple : IWBPXZ,353456789012345,080835#
        """
        return f"IWBPXZ,{imei},{self.generate_journal_no_datetime()}#"
