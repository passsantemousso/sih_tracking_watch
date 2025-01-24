import os
import os
import subprocess
from dotenv import load_dotenv

def is_docker_running():
    """
    Vérifie si le daemon Docker est en marche.
    """
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_running_in_docker():
    """
    Vérifie si l'application est exécutée dans un conteneur Docker.
    """
    # Vérifie le fichier /proc/1/cgroup
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            if 'docker' in f.read() or 'containerd' in f.read():
                return True
    except FileNotFoundError:
        pass

    # Vérifie les variables d'environnement spécifiques à Docker
    if os.getenv('DOCKER_CONTAINER') or os.getenv('AM_I_IN_A_DOCKER_CONTAINER'):
        return True

    return False

def check_docker_run():
    if is_running_in_docker():
        if is_docker_running():
            print("Docker est en marche.")
        else:
            print("Docker n'est pas en marche.")
            load_dotenv()
        print("Application exécutée dans un environnement Docker : load_dotenv() exécuté.")
    else:
        print("Application hors d'un conteneur Docker.")
        load_dotenv()