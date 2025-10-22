import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmanps_alou.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Créer le superuser s'il n'existe pas déjà
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='contact@pharmanps-alou.com',
        password='PharmaNPS2025!'  # CHANGEZ CE MOT DE PASSE !
    )
    print("✅ Superuser créé avec succès!")
    print("Username: ndeye_penda_sarr")
    print("Password: Pensarr12")
else:
    print("ℹ️ Le superuser existe déjà")
