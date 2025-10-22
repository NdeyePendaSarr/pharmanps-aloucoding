from django.urls import path
from . import views

urlpatterns = [
    # Médicaments
    path('medications/', views.medication_list, name='medication_list'),
    path('medications/create/', views.medication_create, name='medication_create'),
    path('medications/<int:pk>/', views.medication_detail, name='medication_detail'),
    path('medications/<int:pk>/update/', views.medication_update, name='medication_update'),
    path('medications/<int:pk>/delete/', views.medication_delete, name='medication_delete'),
    
    # Catégories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    
    # Mouvements de stock
    path('medications/<int:medication_pk>/stock-movement/', views.stock_movement_create, name='stock_movement_create'),
]