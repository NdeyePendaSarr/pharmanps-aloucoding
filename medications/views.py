from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Medication, Category, StockMovement


@login_required
def medication_list(request):
    """Liste des médicaments avec recherche et filtres"""
    medications = Medication.objects.all()
    categories = Category.objects.all()
    
    # Recherche
    search = request.GET.get('search', '')
    if search:
        medications = medications.filter(
            Q(name__icontains=search) |
            Q(dci__icontains=search) |
            Q(barcode__icontains=search)
        )
    
    # Filtres
    category_filter = request.GET.get('category', '')
    if category_filter:
        medications = medications.filter(category_id=category_filter)
    
    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'low':
        medications = [m for m in medications if m.is_low_stock]
    elif stock_filter == 'expired':
        medications = [m for m in medications if m.is_expired]
    elif stock_filter == 'expiring':
        medications = [m for m in medications if m.is_expiring_soon]
    
    context = {
        'medications': medications,
        'categories': categories,
        'search': search,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
    }
    return render(request, 'medications/medication_list.html', context)


@login_required
def medication_detail(request, pk):
    """Détails d'un médicament"""
    medication = get_object_or_404(Medication, pk=pk)
    movements = medication.movements.all()[:10]  # 10 derniers mouvements
    
    context = {
        'medication': medication,
        'movements': movements,
    }
    return render(request, 'medications/medication_detail.html', context)


@login_required
def medication_create(request):
    """Créer un nouveau médicament"""
    categories = Category.objects.all()
    
    if request.method == 'POST':
        try:
            medication = Medication.objects.create(
                name=request.POST.get('name'),
                dci=request.POST.get('dci'),
                barcode=request.POST.get('barcode'),
                category_id=request.POST.get('category'),
                form=request.POST.get('form'),
                dosage=request.POST.get('dosage'),
                purchase_price=request.POST.get('purchase_price'),
                selling_price=request.POST.get('selling_price'),
                quantity=request.POST.get('quantity', 0),
                min_quantity=request.POST.get('min_quantity', 10),
                expiry_date=request.POST.get('expiry_date'),
                location=request.POST.get('location', ''),
                requires_prescription=request.POST.get('requires_prescription') == 'on',
                description=request.POST.get('description', ''),
                created_by=request.user,
            )
            
            # Gérer l'image si présente
            if request.FILES.get('image'):
                medication.image = request.FILES.get('image')
                medication.save()
            
            messages.success(request, f'Médicament "{medication.name}" créé avec succès ! ✅')
            return redirect('medication_detail', pk=medication.pk)
        
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    context = {
        'categories': categories,
        'form_choices': Medication.FORM_CHOICES,
    }
    return render(request, 'medications/medication_form.html', context)


@login_required
def medication_update(request, pk):
    """Modifier un médicament"""
    medication = get_object_or_404(Medication, pk=pk)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        try:
            medication.name = request.POST.get('name')
            medication.dci = request.POST.get('dci')
            medication.barcode = request.POST.get('barcode')
            medication.category_id = request.POST.get('category')
            medication.form = request.POST.get('form')
            medication.dosage = request.POST.get('dosage')
            medication.purchase_price = request.POST.get('purchase_price')
            medication.selling_price = request.POST.get('selling_price')
            medication.quantity = request.POST.get('quantity')
            medication.min_quantity = request.POST.get('min_quantity')
            medication.expiry_date = request.POST.get('expiry_date')
            medication.location = request.POST.get('location', '')
            medication.requires_prescription = request.POST.get('requires_prescription') == 'on'
            medication.description = request.POST.get('description', '')
            
            # Gérer l'image si présente
            if request.FILES.get('image'):
                medication.image = request.FILES.get('image')
            
            medication.save()
            
            messages.success(request, f'Médicament "{medication.name}" modifié avec succès ! ✅')
            return redirect('medication_detail', pk=medication.pk)
        
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    context = {
        'medication': medication,
        'categories': categories,
        'form_choices': Medication.FORM_CHOICES,
        'is_update': True,
    }
    return render(request, 'medications/medication_form.html', context)


@login_required
def medication_delete(request, pk):
    """Supprimer un médicament"""
    medication = get_object_or_404(Medication, pk=pk)
    
    if request.method == 'POST':
        name = medication.name
        medication.delete()
        messages.success(request, f'Médicament "{name}" supprimé avec succès ! 🗑️')
        return redirect('medication_list')
    
    context = {
        'medication': medication,
    }
    return render(request, 'medications/medication_confirm_delete.html', context)


@login_required
def category_list(request):
    """Liste des catégories"""
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
    }
    return render(request, 'medications/category_list.html', context)


@login_required
def category_create(request):
    """Créer une catégorie"""
    if request.method == 'POST':
        try:
            category = Category.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
            )
            messages.success(request, f'Catégorie "{category.name}" créée avec succès ! ✅')
            return redirect('category_list')
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    return render(request, 'medications/category_form.html')


@login_required
def category_update(request, pk):
    """Modifier une catégorie existante"""
    # Récupérer la catégorie ou renvoyer une erreur 404
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        try:
            # Mettre à jour les champs de la catégorie
            category.name = request.POST.get('name')
            category.description = request.POST.get('description', '')
            
            category.save()
            
            messages.success(request, f'Catégorie "{category.name}" modifiée avec succès ! ✏️')
            return redirect('category_list')
        
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')

    context = {
        # Passer l'objet 'category' pour pré-remplir le formulaire
        'category': category, 
        # Indicateur pour personnaliser le titre du template category_form.html
        'is_update': True, 
    }
    # Réutilisation du template d'ajout/modification
    return render(request, 'medications/category_form.html', context)


@login_required
def category_delete(request, pk):
    """Supprimer une catégorie (écran de confirmation)"""
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        try:
            name = category.name
            category.delete()
            messages.success(request, f'Catégorie "{name}" supprimée avec succès ! 🗑️')
            return redirect('category_list')
        except Exception as e:
            # Gérer les erreurs (ex: contrainte de clé étrangère si des médicaments existent)
            messages.error(request, f'Erreur lors de la suppression : {str(e)}')
            return redirect('category_list') # Rediriger vers la liste en cas d'erreur
    
    context = {
        # Passer l'objet 'category' pour l'affichage du nom à confirmer
        'category': category, 
        'object': category, # Utilisation de 'object' pour compatibilité avec le template de suppression
    }
    # Utilisation du template de confirmation de suppression
    return render(request, 'medications/category_confirm_delete.html', context)


@login_required
def stock_movement_create(request, medication_pk):
    """Créer un mouvement de stock"""
    medication = get_object_or_404(Medication, pk=medication_pk)
    
    if request.method == 'POST':
        try:
            StockMovement.objects.create(
                medication=medication,
                movement_type=request.POST.get('movement_type'),
                quantity=int(request.POST.get('quantity')),
                reason=request.POST.get('reason', ''),
                reference=request.POST.get('reference', ''),
                created_by=request.user,
            )
            messages.success(request, 'Mouvement de stock enregistré avec succès ! ✅')
            return redirect('medication_detail', pk=medication.pk)
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')
    
    context = {
        'medication': medication,
        'movement_types': StockMovement.MOVEMENT_TYPES,
    }
    return render(request, 'medications/stock_movement_form.html', context)
