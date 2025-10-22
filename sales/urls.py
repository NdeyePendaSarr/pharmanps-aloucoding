from django.urls import path
from . import views

urlpatterns = [
    # Point de vente
    path('pos/', views.pos_view, name='pos'),
    path('api/search-medication/', views.search_medication, name='search_medication'),
    path('api/create-sale/', views.create_sale, name='create_sale'),
    
    # Ventes
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/invoice/', views.sale_invoice, name='sale_invoice'),
    
    # Clients
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
]