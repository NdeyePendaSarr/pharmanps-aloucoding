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
    """Créer une vente"""
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
    """Liste des ventes"""
    sales = Sale.objects.all()
    
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
            messages.success(request, f'Client "{customer.full_name}" créé avec succès ! ✅')
            return redirect('customer_list')
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return render(request, 'sales/customer_form.html')


@login_required
def customer_detail(request, pk):
    """Détails d'un client"""
    customer = get_object_or_404(Customer, pk=pk)
    sales = customer.sales.all()[:10]
    
    # Statistiques
    total_spent = customer.sales.aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'customer': customer,
        'sales': sales,
        'total_spent': total_spent,
    }
    return render(request, 'sales/customer_detail.html', context)