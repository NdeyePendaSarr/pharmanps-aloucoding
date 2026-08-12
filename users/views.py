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
    today_sales = Sale.objects.filter(created_at__date=today)
    total_sales_today = today_sales.aggregate(total=Sum('total'))['total'] or 0
    sales_count_today = today_sales.count()
    
    # Statistiques clients
    total_customers = Customer.objects.count()
    
    context = {
        'total_medications': total_medications,
        'total_sales': sales_count_today,
        'total_sales_amount': total_sales_today,
        'total_customers': total_customers,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'users/dashboard.html', context)