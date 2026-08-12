from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, F
from django.utils import timezone


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} ! 👋')
            return redirect('dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'users/login.html')


def register_view(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if password != password_confirm:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'users/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
            return render(request, 'users/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
            return render(request, 'users/register.html')
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        messages.success(request, 'Compte créé avec succès ! Vous pouvez maintenant vous connecter.')
        return redirect('login')
    
    return render(request, 'users/register.html')


@login_required
def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, 'Vous êtes déconnecté(e). À bientôt ! 👋')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Vue du tableau de bord"""
    from medications.models import Medication
    from sales.models import Sale, Customer
    
    # Statistiques médicaments
    total_medications = Medication.objects.count()
    low_stock_count = Medication.objects.filter(quantity__lte=F('min_quantity')).count()
    
    # Statistiques ventes (aujourd'hui)
    today = timezone.now().date()
    today_sales = Sale.objects.filter(created_at__date=today, status='completee')
    total_sales_today = today_sales.aggregate(total=Sum('total'))['total'] or 0
    sales_count_today = today_sales.count()
    
    # Statistiques clients
    total_customers = Customer.objects.count()

    # --- Données pour les graphiques ---
    import json
    from datetime import timedelta
    from sales.models import SaleItem

    # 1) Évolution des ventes sur les 7 derniers jours
    labels_jours = []
    donnees_ventes = []
    for i in range(6, -1, -1):
        jour = today - timedelta(days=i)
        total_jour = Sale.objects.filter(
            created_at__date=jour, status='completee'
        ).aggregate(total=Sum('total'))['total'] or 0
        labels_jours.append(jour.strftime('%d/%m'))
        donnees_ventes.append(float(total_jour))

    # 2) Top 5 des médicaments les plus vendus (par quantité)
    from django.db.models import Sum as SumAgg
    top_items = (
        SaleItem.objects
        .values('medication__name')
        .annotate(qte=SumAgg('quantity'))
        .order_by('-qte')[:5]
    )
    labels_produits = [t['medication__name'] for t in top_items]
    donnees_produits = [int(t['qte']) for t in top_items]

    # --- Cumuls du chiffre d'affaires par période (ventes complétées) ---
    from datetime import timedelta as _td
    ventes_ok = Sale.objects.filter(status='completee')

    debut_semaine = today - _td(days=today.weekday())   # lundi de cette semaine
    debut_mois = today.replace(day=1)

    ca_jour = ventes_ok.filter(created_at__date=today).aggregate(t=Sum('total'))['t'] or 0
    ca_semaine = ventes_ok.filter(created_at__date__gte=debut_semaine).aggregate(t=Sum('total'))['t'] or 0
    ca_mois = ventes_ok.filter(created_at__date__gte=debut_mois).aggregate(t=Sum('total'))['t'] or 0
    ca_total = ventes_ok.aggregate(t=Sum('total'))['t'] or 0

    # Détail jour par jour des 7 derniers jours (pour le tableau récapitulatif)
    recap_jours = []
    for i in range(6, -1, -1):
        jour = today - _td(days=i)
        montant = ventes_ok.filter(created_at__date=jour).aggregate(t=Sum('total'))['t'] or 0
        nb = ventes_ok.filter(created_at__date=jour).count()
        recap_jours.append({
            'date': jour.strftime('%d/%m/%Y'),
            'montant': float(montant),
            'nombre': nb,
        })
    recap_jours.reverse()  # plus récent en premier

    context = {
        'total_medications': total_medications,
        'total_sales': sales_count_today,
        'total_sales_amount': total_sales_today,
        'total_customers': total_customers,
        'low_stock_count': low_stock_count,
        # graphiques (sérialisés en JSON pour le template)
        'chart_sales_labels': json.dumps(labels_jours),
        'chart_sales_data': json.dumps(donnees_ventes),
        'chart_products_labels': json.dumps(labels_produits),
        'chart_products_data': json.dumps(donnees_produits),
        # cumuls par période
        'ca_jour': ca_jour,
        'ca_semaine': ca_semaine,
        'ca_mois': ca_mois,
        'ca_total': ca_total,
        'recap_jours': recap_jours,
    }
    return render(request, 'users/dashboard.html', context)