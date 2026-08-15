from django.contrib import admin
from .models import Customer, Sale, SaleItem, Prescription


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'customer_type', 'loyalty_points', 'current_credit', 'credit_limit')
    list_filter = ('customer_type',)
    search_fields = ('first_name', 'last_name', 'phone', 'email')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('sale_number', 'customer', 'total', 'payment_method', 'status', 'created_at', 'created_by')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('sale_number', 'customer__first_name', 'customer__last_name')
    readonly_fields = ('sale_number', 'subtotal', 'discount_amount', 'total', 'change_amount', 'created_at')
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'medication', 'quantity', 'unit_price', 'subtotal')
    search_fields = ('sale__sale_number', 'medication__name')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'doctor_name', 'prescription_date', 'sale', 'created_at')
    list_filter = ('prescription_date',)
    search_fields = ('customer__first_name', 'customer__last_name', 'doctor_name')
