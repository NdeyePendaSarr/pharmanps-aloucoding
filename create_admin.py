import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmanps_alou.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# ✅ CRÉER ADMIN UNIQUEMENT S'IL N'EXISTE PAS
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@pharmanps-alou.com',
        password='VotreMotDePasseForte123!'
    )
    print("✅ Superuser créé")
else:
    print("ℹ️  Superuser existe déjà, aucune création")

# ❌ SUPPRIMEZ TOUT CODE QUI CRÉE DES DONNÉES DE TEST ICI
# Exemple de code à SUPPRIMER :
# if not Medication.objects.exists():
#     Medication.objects.create(...)