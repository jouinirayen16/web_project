from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# Create your models here.
class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=10, unique=True)
    type_vehicule = models.CharField(
        max_length=50,
        choices=[
            ('camionnette', 'camionnette'),
            ('fourgon', 'fourgon'),
            ('camion_porteur', 'Camion Porteur'),
            ('semi_remorque', 'Semi-remorque.')
        ]
    )
    capacite_kg = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="La capacité ne peut pas être nulle.")]
    )
    disponible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entreprise = models.ForeignKey(
        'EntrepriseApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='vehicules'
    )

    def clean(self):
        super().clean()
        if self.entreprise and self.entreprise.type_entreprise != 'transporteur':
            raise ValidationError("L'entreprise doit être de type transporteur.")

    