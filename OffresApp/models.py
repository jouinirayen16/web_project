from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Offer(models.Model):
    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Le prix doit être strictement supérieur à 0.")]
    )
    date_proposition = models.DateField(auto_now_add=True)
    delai_jours = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="Le délai en jours doit être supérieur ou égal à 1.")]
    )
    statut = models.CharField(
        max_length=20,
        choices=[
            ('proposee', 'proposee'),
            ('acceptee', 'acceptee'),
            ('refusee', 'refusee'),
            ('retiree', 'retiree')
        ],
        default='proposee'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transporteur = models.ForeignKey('EntrepriseApp.Entreprise', on_delete=models.CASCADE, related_name='offres')
    expedition = models.ForeignKey('ExpeditionsApp.Expedition', on_delete=models.CASCADE, related_name='offres')
    vehicule = models.ForeignKey('VehiculesApp.Vehicule', on_delete=models.CASCADE, related_name='offres')

