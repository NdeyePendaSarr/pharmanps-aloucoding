# Fichier: sales/views.py 

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from .models import Sale, SaleItem, Customer
from medications.models import Medication
import json


@login_required
def pos_view(request):
    """Interface de Point de Vente (POS)"""
    medications = Medication.objects.filter(quantity__gt=0)
    customers = Customer.objects.all()
    
    context = {
        'medications': medications,
        'customers': customers,
    }
    return render(request, 'sales/pos.html', context)


@login_required
def search_medication(request):
    """API de recherche de médicaments pour le POS"""
    query = request.GET.get('q', '')
    
    if query:
        medications = Medication.objects.filter(
            Q(name__icontains=query) |
            Q(dci__icontains=query) |
            Q(barcode__icontains=query),
            quantity__gt=0
        )[:10]
        
        results = []
        for med in medications:
            results.append({
                'id': med.id,
                'name': med.name,
                'dci': med.dci,
                'price': float(med.selling_price),
                'quantity': med.quantity,
                'image': med.image.url if med.image else None,
            })
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})


@login_required
def create_sale(request):
    """Créer une vente (API de Finalisation)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Créer la vente
            sale = Sale.objects.create(
                customer_id=data.get('customer_id') if data.get('customer_id') else None,
                subtotal=data.get('subtotal', 0),
                discount_percentage=data.get('discount_percentage', 0),
                payment_method=data.get('payment_method'),
                amount_paid=data.get('amount_paid', 0),
                created_by=request.user,
                # Statut forcé à 'completee' lors de la finalisation
                status='completee',
            )
            
            # Créer les lignes de vente
            for item in data.get('items', []):
                medication = Medication.objects.get(id=item['medication_id'])
                SaleItem.objects.create(
                    sale=sale,
                    medication=medication,
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                )
            
            # Mettre à jour le sous-total
            # Note: La méthode save() du modèle Sale devrait calculer le total
            sale.subtotal = sum(item.subtotal for item in sale.items.all())
            sale.save()
            
            return JsonResponse({
                'success': True,
                'sale_id': sale.id,
                'sale_number': sale.sale_number,
                'message': f'Vente #{sale.sale_number} créée avec succès !'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'success': False}, status=400)


@login_required
def sale_list(request):
    """Liste des ventes (Historique)"""
    # Filtrer UNIQUEMENT les ventes COMPLÉTÉES pour l'historique
    sales = Sale.objects.filter(status='completee').order_by('-created_at')
    
    # Filtres
    search = request.GET.get('search', '')
    if search:
        sales = sales.filter(
            Q(sale_number__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search)
        )
    
    date_filter = request.GET.get('date', '')
    if date_filter:
        sales = sales.filter(created_at__date=date_filter)
    
    # Statistiques
    total_sales = sales.aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
        'search': search,
    }
    return render(request, 'sales/sale_list.html', context)


@login_required
def sale_detail(request, pk):
    """Détails d'une vente"""
    sale = get_object_or_404(Sale, pk=pk)
    
    context = {
        'sale': sale,
    }
    return render(request, 'sales/sale_detail.html', context)


@login_required
def sale_invoice(request, pk):
    """Générer une facture"""
    sale = get_object_or_404(Sale, pk=pk)
    
    context = {
        'sale': sale,
    }
    return render(request, 'sales/invoice.html', context)


@login_required
def customer_list(request):
    """Liste des clients"""
    customers = Customer.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone__icontains=search)
        )
    
    context = {
        'customers': customers,
        'search': search,
    }
    return render(request, 'sales/customer_list.html', context)


@login_required
def customer_create(request):
    """Créer un client"""
    if request.method == 'POST':
        try:
            customer = Customer.objects.create(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                phone=request.POST.get('phone'),
                email=request.POST.get('email', ''),
                address=request.POST.get('address', ''),
                date_of_birth=request.POST.get('date_of_birth') or None,
                customer_type=request.POST.get('customer_type', 'particulier'),
                medical_conditions=request.POST.get('medical_conditions', ''),
                credit_limit=request.POST.get('credit_limit', 0),
            )
            messages.success(request, f'Client "{customer.full_name}" créé avec succès !')
            return redirect('customer_list')
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return render(request, 'sales/customer_form.html')


@login_required
def customer_detail(request, pk):
    """Détails d'un client"""
    customer = get_object_or_404(Customer, pk=pk)
    # On filtre pour afficher uniquement les 10 dernières ventes complétées
    sales = customer.sales.filter(status='completee').order_by('-created_at')[:10]
    
    # Statistiques: On agrège uniquement le total des ventes complétées
    total_spent = customer.sales.filter(status='completee').aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'customer': customer,
        'sales': sales,
        'total_spent': total_spent,
    }
    return render(request, 'sales/customer_detail.html', context)


# -------------------------------------------------------------------------
# Mise à jour de la logique de customer_update pour la modification (CRUD)
# -------------------------------------------------------------------------

@login_required
def customer_update(request, pk):
    """Mise à jour du client existant"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        try:
            # 1. Récupérer et mettre à jour les champs de l'objet customer
            customer.first_name = request.POST.get('first_name')
            customer.last_name = request.POST.get('last_name')
            customer.phone = request.POST.get('phone')
            customer.email = request.POST.get('email', '')
            customer.address = request.POST.get('address', '')
            
            # Gérer le champ de date (peut être None)
            date_of_birth_str = request.POST.get('date_of_birth')
            customer.date_of_birth = date_of_birth_str if date_of_birth_str else None
            
            customer.customer_type = request.POST.get('customer_type', 'particulier')
            customer.medical_conditions = request.POST.get('medical_conditions', '')
            
            # Gérer le champ numérique (DecimalField): s'assurer que c'est un nombre
            credit_limit_str = request.POST.get('credit_limit')
            try:
                # Convertir en Decimal (ou float)
                customer.credit_limit = float(credit_limit_str)
            except (ValueError, TypeError):
                customer.credit_limit = 0
            
            # 2. Sauvegarder l'objet mis à jour dans la base de données
            customer.save()
            
            messages.success(request, f'Client "{customer.full_name}" mis à jour avec succès !')
            return redirect('customer_detail', pk=customer.pk)

        except Exception as e:
            # Gérer les erreurs de validation ou de base de données
            messages.error(request, f'Erreur lors de la mise à jour : {str(e)}')
            
    # Pour la méthode GET (affichage initial avec pré-remplissage) ou en cas d'erreur POST
    context = {
        'customer': customer,
    }
    return render(request, 'sales/customer_form.html', context)


@login_required
def customer_sales(request, pk):
    """Vue pour lister TOUTES les ventes d'un client (implémentation minimale)"""
    customer = get_object_or_404(Customer, pk=pk)
    
    # Récupère toutes les ventes complétées pour ce client
    all_sales = customer.sales.filter(status='completee').order_by('-created_at')
    
    context = {
        'customer': customer,
        'sales': all_sales,
        'total_sales': all_sales.aggregate(total=Sum('total'))['total'] or 0,
    }
    # NOTE: Assurez-vous d'avoir un template 'sales/customer_sales_list.html' ou utilisez 'sales/sale_list.html'
    return render(request, 'sales/sale_list.html', context) # Utilisation temporaire de sale_list.html