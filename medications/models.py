from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Category(models.Model):
    """Catégories de médicaments"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Medication(models.Model):
    """Modèle pour les médicaments"""
    
    FORM_CHOICES = [
        ('comprimé', 'Comprimé'),
        ('gélule', 'Gélule'),
        ('sirop', 'Sirop'),
        ('injection', 'Injection'),
        ('inhalateur', 'Inhalateur'),
        ('pommade', 'Pommade'),
        ('crème', 'Crème'),
        ('suppositoire', 'Suppositoire'),
        ('collyre', 'Collyre'),
        ('solution', 'Solution'),
    ]
    
    # Informations de base
    name = models.CharField(max_length=200, verbose_name="Nom commercial")
    dci = models.CharField(max_length=200, verbose_name="DCI", help_text="Dénomination Commune Internationale")
    barcode = models.CharField(max_length=100, unique=True, verbose_name="Code-barres")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='medications', verbose_name="Catégorie")
    
    # Forme et dosage
    form = models.CharField(max_length=50, choices=FORM_CHOICES, verbose_name="Forme galénique")
    dosage = models.CharField(max_length=100, verbose_name="Dosage", help_text="Ex: 500mg, 10ml")
    
    # Prix
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix d'achat")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de vente")
    
    # Stock
    quantity = models.IntegerField(default=0, verbose_name="Quantité en stock")
    min_quantity = models.IntegerField(default=10, verbose_name="Stock minimum", help_text="Seuil d'alerte")
    
    # Dates
    expiry_date = models.DateField(verbose_name="Date de péremption")
    
    # Autres informations
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Emplacement", help_text="Rayon, étagère...")
    requires_prescription = models.BooleanField(default=False, verbose_name="Prescription requise")
    image = CloudinaryField('Image', blank=True, null=True, folder='medications')
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='medications_created', verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Médicament"
        verbose_name_plural = "Médicaments"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.dosage})"
    
    @property
    def is_low_stock(self):
        """Vérifie si le stock est faible"""
        return self.quantity <= self.min_quantity
    
    @property
    def is_expired(self):
        """Vérifie si le médicament est périmé"""
        return self.expiry_date < timezone.now().date()
    
    @property
    def is_expiring_soon(self):
        """Vérifie si le médicament expire dans moins de 30 jours"""
        days_until_expiry = (self.expiry_date - timezone.now().date()).days
        return 0 < days_until_expiry <= 30
    
    @property
    def profit_margin(self):
        """Calcule la marge bénéficiaire"""
        return self.selling_price - self.purchase_price
    
    @property
    def profit_percentage(self):
        """Calcule le pourcentage de marge"""
        if self.purchase_price > 0:
            return ((self.selling_price - self.purchase_price) / self.purchase_price) * 100
        return 0
    
    @property
    def stock_value(self):
        """Calcule la valeur totale du stock"""
        return self.quantity * self.purchase_price


class StockMovement(models.Model):
    """Historique des mouvements de stock"""
    
    MOVEMENT_TYPES = [
        ('entrée', 'Entrée'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement'),
        ('retour', 'Retour'),
        ('perte', 'Perte'),
        ('périmé', 'Périmé'),
    ]
    
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='movements', verbose_name="Médicament")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, verbose_name="Type de mouvement")
    quantity = models.IntegerField(verbose_name="Quantité")
    reason = models.TextField(blank=True, null=True, verbose_name="Raison/Justification")
    reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="Référence", help_text="Numéro de bon, facture...")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Effectué par")
    
    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.movement_type} - {self.medication.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        """Mise à jour automatique du stock lors de la sauvegarde"""
        is_new = self.pk is None
        
        if is_new:
            # Nouveau mouvement
            if self.movement_type in ['entrée', 'retour', 'ajustement']:
                self.medication.quantity += self.quantity
            elif self.movement_type in ['sortie', 'perte', 'périmé']:
                self.medication.quantity -= self.quantity
            
            self.medication.save()
        
        super().save(*args, **kwargs)