"""
Script pour remplir la base de donnees avec des donnees de test realistes
Executez : py manage.py shell < populate_db.py
"""
# -*- coding: utf-8 -*-

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Forcer l'encodage UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmanps_alou.settings')
django.setup()

from medications.models import Category, Medication, StockMovement
from sales.models import Customer, Sale, SaleItem
from django.contrib.auth.models import User

print("🚀 Debut du remplissage de la base de donnees...\n")

# 1. CREER DES CATEGORIES
print("📦 Creation des categories...")
categories_data = [
    {'name': 'Anti-asthmatiques', 'description': 'Medicaments pour traiter l\'asthme et les troubles respiratoires'},
    {'name': 'Antibiotiques', 'description': 'Medicaments contre les infections bacteriennes'},
    {'name': 'Antalgiques', 'description': 'Medicaments contre la douleur'},
    {'name': 'Antipyretique', 'description': 'Medicaments contre la fievre'},
    {'name': 'Anti-inflammatoires', 'description': 'Medicaments contre l\'inflammation'},
    {'name': 'Antipaludiques', 'description': 'Medicaments contre le paludisme'},
    {'name': 'Vitamines', 'description': 'Supplements vitaminiques et mineraux'},
    {'name': 'Antihistaminiques', 'description': 'Medicaments contre les allergies'},
    {'name': 'Antidiabetiques', 'description': 'Medicaments pour le diabete'},
    {'name': 'Cardiologie', 'description': 'Medicaments pour le coeur et la tension'},
]

categories = {}
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categories[cat_data['name']] = cat
    print(f"  ✅ {cat.name}")

print(f"\n✅ {len(categories)} categories creees\n")

# 2. CREER DES MEDICAMENTS
print("💊 Creation des medicaments...")

# Obtenir l'utilisateur admin
try:
    admin_user = User.objects.first()
except:
    admin_user = None

medications_data = [
    # Anti-asthmatiques (pour NPS !)
    {'name': 'Ventoline', 'dci': 'Salbutamol', 'barcode': '3400930000001', 'category': 'Anti-asthmatiques', 
     'form': 'inhalateur', 'dosage': '100 mcg', 'purchase_price': 2500, 'selling_price': 3500, 
     'quantity': 50, 'min_quantity': 10, 'location': 'Rayon A - Etagere 1', 'requires_prescription': True},
    
    {'name': 'Symbicort', 'dci': 'Budesonide + Formoterol', 'barcode': '3400930000002', 'category': 'Anti-asthmatiques',
     'form': 'inhalateur', 'dosage': '160/4.5 mcg', 'purchase_price': 5000, 'selling_price': 7000,
     'quantity': 30, 'min_quantity': 8, 'location': 'Rayon A - Etagere 1', 'requires_prescription': True},
    
    {'name': 'Seretide', 'dci': 'Fluticasone + Salmeterol', 'barcode': '3400930000003', 'category': 'Anti-asthmatiques',
     'form': 'inhalateur', 'dosage': '125/25 mcg', 'purchase_price': 6000, 'selling_price': 8500,
     'quantity': 25, 'min_quantity': 5, 'location': 'Rayon A - Etagere 1', 'requires_prescription': True},
    
    # Antibiotiques
    {'name': 'Amoxicilline', 'dci': 'Amoxicilline', 'barcode': '3400930000010', 'category': 'Antibiotiques',
     'form': 'comprime', 'dosage': '500mg', 'purchase_price': 150, 'selling_price': 250,
     'quantity': 200, 'min_quantity': 30, 'location': 'Rayon B - Etagere 2', 'requires_prescription': True},
    
    {'name': 'Augmentin', 'dci': 'Amoxicilline + Acide clavulanique', 'barcode': '3400930000011', 'category': 'Antibiotiques',
     'form': 'comprime', 'dosage': '1g', 'purchase_price': 350, 'selling_price': 550,
     'quantity': 150, 'min_quantity': 25, 'location': 'Rayon B - Etagere 2', 'requires_prescription': True},
    
    {'name': 'Ciprofloxacine', 'dci': 'Ciprofloxacine', 'barcode': '3400930000012', 'category': 'Antibiotiques',
     'form': 'comprime', 'dosage': '500mg', 'purchase_price': 200, 'selling_price': 350,
     'quantity': 100, 'min_quantity': 20, 'location': 'Rayon B - Etagere 3', 'requires_prescription': True},
    
    # Antalgiques
    {'name': 'Paracetamol', 'dci': 'Paracetamol', 'barcode': '3400930000020', 'category': 'Antalgiques',
     'form': 'comprime', 'dosage': '500mg', 'purchase_price': 50, 'selling_price': 100,
     'quantity': 500, 'min_quantity': 100, 'location': 'Rayon C - Etagere 1', 'requires_prescription': False},
    
    {'name': 'Doliprane', 'dci': 'Paracetamol', 'barcode': '3400930000021', 'category': 'Antalgiques',
     'form': 'comprime', 'dosage': '1000mg', 'purchase_price': 75, 'selling_price': 150,
     'quantity': 400, 'min_quantity': 80, 'location': 'Rayon C - Etagere 1', 'requires_prescription': False},
    
    {'name': 'Ibuprofene', 'dci': 'Ibuprofene', 'barcode': '3400930000022', 'category': 'Anti-inflammatoires',
     'form': 'comprime', 'dosage': '400mg', 'purchase_price': 100, 'selling_price': 200,
     'quantity': 300, 'min_quantity': 50, 'location': 'Rayon C - Etagere 2', 'requires_prescription': False},
    
    {'name': 'Aspirine', 'dci': 'Acide acetylsalicylique', 'barcode': '3400930000023', 'category': 'Antalgiques',
     'form': 'comprime', 'dosage': '500mg', 'purchase_price': 40, 'selling_price': 80,
     'quantity': 600, 'min_quantity': 100, 'location': 'Rayon C - Etagere 2', 'requires_prescription': False},
    
    # Antipaludiques
    {'name': 'Coartem', 'dci': 'Artemether + Lumefantrine', 'barcode': '3400930000030', 'category': 'Antipaludiques',
     'form': 'comprime', 'dosage': '20/120mg', 'purchase_price': 800, 'selling_price': 1200,
     'quantity': 120, 'min_quantity': 30, 'location': 'Rayon D - Etagere 1', 'requires_prescription': True},
    
    {'name': 'Malarone', 'dci': 'Atovaquone + Proguanil', 'barcode': '3400930000031', 'category': 'Antipaludiques',
     'form': 'comprime', 'dosage': '250/100mg', 'purchase_price': 1500, 'selling_price': 2200,
     'quantity': 80, 'min_quantity': 15, 'location': 'Rayon D - Etagere 1', 'requires_prescription': True},
    
    # Vitamines
    {'name': 'Vitamine C', 'dci': 'Acide ascorbique', 'barcode': '3400930000040', 'category': 'Vitamines',
     'form': 'comprime', 'dosage': '500mg', 'purchase_price': 150, 'selling_price': 300,
     'quantity': 200, 'min_quantity': 40, 'location': 'Rayon E - Etagere 1', 'requires_prescription': False},
    
    {'name': 'Multivitamines', 'dci': 'Complexe multivitamine', 'barcode': '3400930000041', 'category': 'Vitamines',
     'form': 'comprime', 'dosage': '1 comprime/jour', 'purchase_price': 500, 'selling_price': 800,
     'quantity': 150, 'min_quantity': 30, 'location': 'Rayon E - Etagere 1', 'requires_prescription': False},
    
    # Antihistaminiques
    {'name': 'Cetirizine', 'dci': 'Cetirizine', 'barcode': '3400930000050', 'category': 'Antihistaminiques',
     'form': 'comprime', 'dosage': '10mg', 'purchase_price': 100, 'selling_price': 200,
     'quantity': 180, 'min_quantity': 35, 'location': 'Rayon F - Etagere 1', 'requires_prescription': False},
    
    {'name': 'Loratadine', 'dci': 'Loratadine', 'barcode': '3400930000051', 'category': 'Antihistaminiques',
     'form': 'sirop', 'dosage': '5mg/5ml', 'purchase_price': 250, 'selling_price': 400,
     'quantity': 100, 'min_quantity': 20, 'location': 'Rayon F - Etagere 2', 'requires_prescription': False},
    
    # Medicaments en stock faible (pour tester les alertes)
    {'name': 'Azithromycine', 'dci': 'Azithromycine', 'barcode': '3400930000060', 'category': 'Antibiotiques',
     'form': 'comprime', 'dosage': '500mg', 'purchase_price': 400, 'selling_price': 650,
     'quantity': 8, 'min_quantity': 20, 'location': 'Rayon B - Etagere 3', 'requires_prescription': True},
    
    {'name': 'Omeprazole', 'dci': 'Omeprazole', 'barcode': '3400930000070', 'category': 'Anti-inflammatoires',
     'form': 'gelule', 'dosage': '20mg', 'purchase_price': 150, 'selling_price': 300,
     'quantity': 5, 'min_quantity': 15, 'location': 'Rayon G - Etagere 1', 'requires_prescription': False},
]
medications = {}
today = datetime.now().date()

for med_data in medications_data:
    # Date de peremption aleatoire (entre 6 mois et 2 ans)
    expiry_date = today + timedelta(days=180 + (med_data['quantity'] * 2))
    
    med, created = Medication.objects.get_or_create(
        barcode=med_data['barcode'],
        defaults={
            'name': med_data['name'],
            'dci': med_data['dci'],
            'category': categories[med_data['category']],
            'form': med_data['form'],
            'dosage': med_data['dosage'],
            'purchase_price': Decimal(str(med_data['purchase_price'])),
            'selling_price': Decimal(str(med_data['selling_price'])),
            'quantity': med_data['quantity'],
            'min_quantity': med_data['min_quantity'],
            'expiry_date': expiry_date,
            'location': med_data['location'],
            'requires_prescription': med_data['requires_prescription'],
            'created_by': admin_user,
        }
    )
    medications[med_data['name']] = med
    print(f"  ✅ {med.name} - {med.dosage}")

print(f"\n✅ {len(medications)} medicaments crees\n")

# 3. CREER DES CLIENTS
print("👥 Creation des clients...")

customers_data = [
    {
        'first_name': 'Fatou',
        'last_name': 'Diop',
        'phone': '+221 77 123 45 67',
        'email': 'fatou.diop@email.com',
        'address': 'Ouakam, Dakar',
        'customer_type': 'particulier',
        'medical_conditions': 'Asthme chronique, allergie a la penicilline',
        'credit_limit': 50000,
    },
    {
        'first_name': 'Amadou',
        'last_name': 'Ba',
        'phone': '+221 78 234 56 78',
        'email': 'amadou.ba@email.com',
        'address': 'Plateau, Dakar',
        'customer_type': 'particulier',
        'medical_conditions': 'Diabete type 2, hypertension',
        'credit_limit': 75000,
    },
    {
        'first_name': 'Aissatou',
        'last_name': 'Sow',
        'phone': '+221 70 345 67 89',
        'email': 'aissatou.sow@email.com',
        'address': 'Almadies, Dakar',
        'customer_type': 'particulier',
        'medical_conditions': '',
        'credit_limit': 30000,
    },
    {
        'first_name': 'Moussa',
        'last_name': 'Ndiaye',
        'phone': '+221 76 456 78 90',
        'email': 'moussa.ndiaye@email.com',
        'address': 'Mermoz, Dakar',
        'customer_type': 'particulier',
        'medical_conditions': 'Asthme leger',
        'credit_limit': 40000,
    },
    {
        'first_name': 'Entreprise ABC',
        'last_name': 'SARL',
        'phone': '+221 33 123 45 67',
        'email': 'contact@abc.sn',
        'address': 'Zone Industrielle, Dakar',
        'customer_type': 'entreprise',
        'medical_conditions': '',
        'credit_limit': 200000,
    },
    {
        'first_name': 'Assurance',
        'last_name': 'IPRESS',
        'phone': '+221 33 234 56 78',
        'email': 'ipress@assurance.sn',
        'address': 'Centre-ville, Dakar',
        'customer_type': 'assurance',
        'medical_conditions': '',
        'credit_limit': 500000,
    },
]

customers = []
for cust_data in customers_data:
    customer, created = Customer.objects.get_or_create(
        phone=cust_data['phone'],
        defaults=cust_data
    )
    customers.append(customer)
    print(f"  ✅ {customer.full_name} ({customer.phone})")

print(f"\n✅ {len(customers)} clients crees\n")

# 4. CREER DES VENTES
print("🛒 Creation de ventes d'exemple...")

# Vente 1 : Asthme (Fatou)
sale1 = Sale.objects.create(
    customer=customers[0],
    payment_method='especes',
    amount_paid=12000,
    created_by=admin_user,
)
SaleItem.objects.create(
    sale=sale1,
    medication=medications['Ventoline'],
    quantity=2,
    unit_price=medications['Ventoline'].selling_price,
)
SaleItem.objects.create(
    sale=sale1,
    medication=medications['Cetirizine'],
    quantity=1,
    unit_price=medications['Cetirizine'].selling_price,
)
sale1.subtotal = sum(item.subtotal for item in sale1.items.all())
sale1.save()
print(f"  ✅ Vente #{sale1.sale_number} - {sale1.total} FCFA")

# Vente 2 : Grippe (Amadou)
sale2 = Sale.objects.create(
    customer=customers[1],
    payment_method='carte',
    amount_paid=0,
    created_by=admin_user,
)
SaleItem.objects.create(
    sale=sale2,
    medication=medications['Paracetamol'],
    quantity=3,
    unit_price=medications['Paracetamol'].selling_price,
)
SaleItem.objects.create(
    sale=sale2,
    medication=medications['Vitamine C'],
    quantity=2,
    unit_price=medications['Vitamine C'].selling_price,
)
sale2.subtotal = sum(item.subtotal for item in sale2.items.all())
sale2.save()
print(f"  ✅ Vente #{sale2.sale_number} - {sale2.total} FCFA")

# Vente 3 : Paludisme (Client anonyme)
sale3 = Sale.objects.create(
    customer=None,
    payment_method='mobile_money',
    amount_paid=0,
    created_by=admin_user,
)
SaleItem.objects.create(
    sale=sale3,
    medication=medications['Coartem'],
    quantity=1,
    unit_price=medications['Coartem'].selling_price,
)
SaleItem.objects.create(
    sale=sale3,
    medication=medications['Doliprane'],
    quantity=2,
    unit_price=medications['Doliprane'].selling_price,
)
sale3.subtotal = sum(item.subtotal for item in sale3.items.all())
sale3.save()
print(f"  ✅ Vente #{sale3.sale_number} - {sale3.total} FCFA")

print(f"\n✅ 3 ventes crees\n")

# 5. RESUME
print("=" * 60)
print("✅ BASE DE DONNEES REMPLIE AVEC SUCCES !")
print("=" * 60)
print(f"\n📊 STATISTIQUES :")
print(f"  • Categories : {Category.objects.count()}")
print(f"  • Medicaments : {Medication.objects.count()}")
print(f"  • Clients : {Customer.objects.count()}")
print(f"  • Ventes : {Sale.objects.count()}")
print(f"  • Medicaments en alerte stock : {Medication.objects.filter(quantity__lte=10).count()}")
print(f"\n🎯 Vous pouvez maintenant tester l'application !")
print(f"   Dashboard : http://127.0.0.1:8000/dashboard/")
print(f"   POS : http://127.0.0.1:8000/pos/")
print(f"   Medicaments : http://127.0.0.1:8000/medications/")
print(f"   Clients : http://127.0.0.1:8000/customers/")
print(f"   Ventes : http://127.0.0.1:8000/sales/")
print("\n" + "=" * 60)
