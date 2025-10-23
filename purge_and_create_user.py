import os
import django
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmanps_alou.settings')
django.setup()

User = get_user_model()

# Utilisateur à créer (sans espaces pour plus de fiabilité)
NEW_USERNAME = 'ndeye_penda_sarr'
EMAIL = 'sndeyependa27@gmail.com'
PASSWORD = 'Pensarr@12#' 

# --------------------------------------------------------
# 1. SUPPRIMER LES UTILISATEURS PROBLÉMATIQUES (S'ILS EXISTENT)
# --------------------------------------------------------
# Supprimer l'utilisateur "admin" si c'est celui qui bloque la création
User.objects.filter(username='admin').delete()
print(f"🗑️ Utilisateur 'admin' purgé (s'il existait).")

# Supprimer l'ancienne tentative de création avec espaces
User.objects.filter(username='Ndeye Penda SARR').delete()
print(f"🗑️ Utilisateur 'Ndeye Penda SARR' purgé (s'il existait).")


# --------------------------------------------------------
# 2. CRÉER LE NOUVEL UTILISATEUR GARANTI
# --------------------------------------------------------
try:
    if not User.objects.filter(username=NEW_USERNAME).exists():
        User.objects.create_superuser(
            username=NEW_USERNAME,
            email=EMAIL,
            password=PASSWORD
        )
        print(f"✅ Superuser '{NEW_USERNAME}' créé avec succès!")
    else:
        # Si l'utilisateur existe déjà (par exemple, après un précédent succès), 
        # on garantit que le mot de passe est le bon en le réinitialisant.
        user = User.objects.get(username=NEW_USERNAME)
        user.set_password(PASSWORD)
        user.save()
        print(f"✅ Mot de passe de l'utilisateur '{NEW_USERNAME}' réinitialisé.")

except IntegrityError as e:
    print(f"❌ Erreur d'intégrité lors de la création : {e}")