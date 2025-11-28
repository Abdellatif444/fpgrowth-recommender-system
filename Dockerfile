# Utiliser une image Python officielle légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY backend/requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code du projet
COPY . .

# Exposer le port 7860 (Port par défaut de Hugging Face)
EXPOSE 7860

# Définir les variables d'environnement par défaut
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production
ENV PORT=7860

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--chdir", "backend", "app:app"]
