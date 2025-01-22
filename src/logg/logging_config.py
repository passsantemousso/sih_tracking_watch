import logging
import logging.handlers


# Configuration globale du logging
def configure_logging(log_file="system.log"):
    # Formatter pour structurer les messages de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler pour écrire dans un fichier
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # Niveau minimal pour écrire dans le fichier
    file_handler.setFormatter(formatter)

    # Handler pour afficher dans la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Niveau minimal pour la console
    console_handler.setFormatter(formatter)

    # Configurer le logger racine
    logging.basicConfig(
        level=logging.DEBUG,  # Niveau global
        handlers=[file_handler, console_handler]  # Ajouter les handlers
    )
