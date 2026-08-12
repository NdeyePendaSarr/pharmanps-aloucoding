"""
Crée un compte superuser à partir de variables d'environnement,
uniquement s'il n'existe pas déjà. Sûr à lancer à chaque déploiement.

Variables attendues (définies dans Render → Environment) :
  ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Crée le superuser initial depuis les variables d'environnement (idempotent)."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("ADMIN_USERNAME")
        email = os.environ.get("ADMIN_EMAIL", "")
        password = os.environ.get("ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_USERNAME ou ADMIN_PASSWORD absent — création du superuser ignorée."
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(
                f"Le superuser '{username}' existe déjà — rien à faire."
            ))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(
            f"Superuser '{username}' créé avec succès."
        ))
