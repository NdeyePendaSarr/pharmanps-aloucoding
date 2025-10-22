import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmanps_alou.settings')
django.setup()

from medications.models import Medication

# Liste des corrections
corrections = {
    'OmÃ©prazole': 'Omeprazole',
    'ParacÃ©tamol': 'Paracetamol', 
    'AzÃ©ithromycine': 'Azithromycine',
    'CÃ©tirizine': 'Cetirizine',
    'comprimÃ©': 'comprime',
    'gÃ©lule': 'gelule',
}

meds = Medication.objects.all()
count = 0

for med in meds:
    updated = False
    
    # Corriger le nom
    for bad, good in corrections.items():
        if bad in med.name:
            med.name = med.name.replace(bad, good)
            updated = True
        if bad in med.dosage:
            med.dosage = med.dosage.replace(bad, good)
            updated = True
    
    if updated:
        med.save()
        count += 1
        print(f"✅ Corrige: {med.name}")

print(f"\n✅ {count} medicaments corriges!")