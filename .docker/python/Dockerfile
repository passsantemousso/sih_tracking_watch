# Utiliser l'image officielle de Python 3.11
FROM python:3.11-slim

# Mettre à jour l'image et installer les dépendances de base
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    libssl-dev \
    libsasl2-dev \
    liblz4-dev \
    zlib1g-dev \
    make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY ./tcp_server /app

# Copier les fichiers nécessaires
COPY ./tcp_server/requirements.txt /app/requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Définir PYTHONPATH
ENV PYTHONPATH=/app

# Exposer le port utilisé par votre serveur TCP
EXPOSE 6020

# Lancer le serveur TCP
CMD ["python", "tcp_server_app.py"]
