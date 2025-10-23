# compare_stats.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmanps_alou.settings')
django.setup()

from medications.models import Medication
from sales.models import Sale, Customer
from django.db.models import Sum
import json
from datetime import datetime

stats = {
    'timestamp': datetime.now().isoformat(),
    'medications': {
        'total': Medication.objects.count(),
        'low_stock': Medication.objects.filter(quantity__lte=5).count(),
        'list': list(Medication.objects.values('id', 'name', 'quantity', 'created_at'))
    },
    'sales': {
        'total': Sale.objects.count(),
        'total_revenue': Sale.objects.aggregate(Sum('total'))['total__sum'] or 0,
        'list': list(Sale.objects.values('id', 'sale_number', 'total', 'created_at').order_by('-created_at')[:10])
    },
    'customers': {
        'total': Customer.objects.count()
    }
}

# Sauvegarder dans un fichier
with open('stats_snapshot.json', 'w') as f:
    json.dump(stats, f, indent=2, default=str)

print("📊 SNAPSHOT DES STATISTIQUES")
print(f"Médicaments : {stats['medications']['total']}")
print(f"Stock faible : {stats['medications']['low_stock']}")
print(f"Ventes : {stats['sales']['total']}")
print(f"CA total : {stats['sales']['total_revenue']} FCFA")
print(f"Clients : {stats['customers']['total']}")
print(f"\n✅ Snapshot sauvegardé dans stats_snapshot.json")