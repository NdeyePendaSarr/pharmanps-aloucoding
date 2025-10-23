"""
Script pour vérifier les doublons et données suspectes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmanps_alou.settings')
django.setup()

from medications.models import Medication
from sales.models import Sale
from django.db.models import Count

print("🔍 DIAGNOSTIC DES DONNÉES\n")

# 1. Vérifier les doublons de médicaments
print("📊 MÉDICAMENTS DUPLIQUÉS (même code-barres) :")
duplicates = Medication.objects.values('barcode').annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicates:
    for dup in duplicates:
        meds = Medication.objects.filter(barcode=dup['barcode'])
        print(f"  ⚠️  Code-barres: {dup['barcode']} - {dup['count']} occurrences")
        for med in meds:
            print(f"     - ID: {med.id} | {med.name} | Créé: {med.created_at}")
else:
    print("  ✅ Aucun doublon détecté")

print()

# 2. Vérifier les ventes récentes
print("📊 VENTES DES 24 DERNIÈRES HEURES :")
from datetime import datetime, timedelta
recent_sales = Sale.objects.filter(
    created_at__gte=datetime.now() - timedelta(days=1)
).order_by('-created_at')

if recent_sales:
    for sale in recent_sales:
        print(f"  💰 {sale.sale_number} - {sale.total} FCFA - {sale.created_at}")
else:
    print("  ℹ️  Aucune vente récente")

print()

# 3. Statistiques générales
print("📊 STATISTIQUES GÉNÉRALES :")
print(f"  Total médicaments : {Medication.objects.count()}")
print(f"  Total ventes : {Sale.objects.count()}")
print(f"  Médicaments stock faible : {Medication.objects.filter(quantity__lte=5).count()}")

print()

# 4. Dernières créations
print("📊 DERNIÈRES CRÉATIONS :")
latest_meds = Medication.objects.order_by('-created_at')[:5]
for med in latest_meds:
    print(f"  💊 {med.name} - Créé: {med.created_at}")