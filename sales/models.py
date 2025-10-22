from django.db import models
from django.contrib.auth.models import User
from medications.models import Medication
from django.utils import timezone


class Customer(models.Model):
    """Modèle pour les clients"""
    
    CUSTOMER_TYPES = [
        ('particulier', 'Particulier'),
        ('entreprise', 'Entreprise'),
        ('assurance', 'Assurance'),
    ]
    
    # Informations de base
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(blank=True, null=True, verbose_name="Adresse")
    
    # Informations complémentaires
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='particulier', verbose_name="Type de client")
    medical_conditions = models.TextField(blank=True, null=True, verbose_name="Conditions médicales", help_text="Allergies, maladies chroniques comme l'asthme, etc.")
    
    # Programme de fidélité
    loyalty_points = models.IntegerField(default=0, verbose_name="Points de fidélité")
    
    # Crédit
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Limite de crédit")
    current_credit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Crédit actuel")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def available_credit(self):
        """Crédit disponible"""
        return self.credit_limit - self.current_credit


class Sale(models.Model):
    """Modèle pour les ventes"""
    
    PAYMENT_METHODS = [
        ('especes', 'Espèces'),
        ('carte', 'Carte bancaire'),
        ('mobile_money', 'Mobile Money'),
        ('credit', 'Crédit'),
    ]
    
    STATUS_CHOICES = [
        ('en_cours', 'En cours'),
        ('completee', 'Complétée'),
        ('annulee', 'Annulée'),
    ]
    
    # Informations de base
    sale_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de vente")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales', verbose_name="Client")
    
    # Montants
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Sous-total")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Remise (%)")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant remise")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total")
    
    # Paiement
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="Mode de paiement")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant payé")
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Monnaie rendue")
    
    # Statut
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completee', verbose_name="Statut")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de vente")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Vendu par")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Vente #{self.sale_number}"
    
    def save(self, *args, **kwargs):
        # Générer un numéro de vente automatique
        if not self.sale_number:
            today = timezone.now().date()
            count = Sale.objects.filter(created_at__date=today).count() + 1
            self.sale_number = f"V{today.strftime('%Y%m%d')}{count:04d}"
        
        # Calculer les montants
        self.discount_amount = (self.subtotal * self.discount_percentage) / 100
        self.total = self.subtotal - self.discount_amount
        
        # Calculer la monnaie
        if self.amount_paid > self.total:
            self.change_amount = self.amount_paid - self.total
        
        super().save(*args, **kwargs)
    
    @property
    def profit(self):
        """Calcul du bénéfice"""
        total_cost = sum(item.medication.purchase_price * item.quantity for item in self.items.all())
        return self.total - total_cost


class SaleItem(models.Model):
    """Lignes d'une vente"""
    
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name="Vente")
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT, verbose_name="Médicament")
    quantity = models.IntegerField(verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sous-total")
    
    class Meta:
        verbose_name = "Ligne de vente"
        verbose_name_plural = "Lignes de vente"
    
    def __str__(self):
        return f"{self.medication.name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculer le sous-total
        self.subtotal = self.unit_price * self.quantity
        
        # Mettre à jour le stock du médicament (si nouvelle ligne)
        if not self.pk:
            self.medication.quantity -= self.quantity
            self.medication.save()
            
            # Créer un mouvement de stock
            from medications.models import StockMovement
            StockMovement.objects.create(
                medication=self.medication,
                movement_type='sortie',
                quantity=self.quantity,
                reason=f"Vente #{self.sale.sale_number}",
                reference=self.sale.sale_number,
                created_by=self.sale.created_by
            )
        
        super().save(*args, **kwargs)


class Prescription(models.Model):
    """Modèle pour les ordonnances"""
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='prescriptions', verbose_name="Client")
    sale = models.OneToOneField(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescription', verbose_name="Vente associée")
    
    doctor_name = models.CharField(max_length=200, verbose_name="Nom du médecin")
    prescription_date = models.DateField(verbose_name="Date de prescription")
    prescription_image = models.ImageField(upload_to='prescriptions/', blank=True, null=True, verbose_name="Image de l'ordonnance")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Ordonnance"
        verbose_name_plural = "Ordonnances"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ordonnance - {self.customer.full_name} ({self.prescription_date})"