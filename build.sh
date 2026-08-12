#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Installation des dépendances..."
pip install -r requirements.txt

echo "🎨 Compilation de Tailwind CSS..."
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.1/tailwindcss-linux-x64
chmod +x tailwindcss-linux-x64
./tailwindcss-linux-x64 -i ./static/css/input.css -o ./static/css/output.css --minify

echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "🗄️ Application des migrations..."
python manage.py migrate

echo "👤 Création du compte admin (si absent)..."
python manage.py init_admin

echo "✅ Build terminé avec succès!"