FROM python:3.11-slim
LABEL authors="effijeanmermoz"

# Installation des dépendances système
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

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application dans l'image
COPY ./app /app

# Copier le fichier des dépendances Python
COPY ./app/requirements.txt /app/requirements.txt

# Installer pip et les dépendances Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Définir PYTHONPATH
ENV PYTHONPATH=/app

# Exposer le port
EXPOSE 80

# Lancer l'application avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
