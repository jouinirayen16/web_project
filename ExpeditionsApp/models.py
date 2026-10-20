from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

class Expedition(models.Model):
    reference = models.CharField(max_length=20, unique=True, editable=False)
    ville_depart = models.CharField(max_length=100)
    ville_arrive = models.CharField(max_length=100)
    date_souhaitee = models.DateField()
    poids_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Le poids ne peut pas être nul.")]
    )
    description = models.TextField()
    statut = models.CharField(
        max_length=20,
        choices=[
            ('publiee', 'publiee'),
            ('attribuee', 'attribuee'),
            ('en_cours', 'en_cours'),
            ('livree', 'livree'),
            ('annulee', 'annulee')
        ],
        default='publiee'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entreprise = models.ForeignKey(
        'EntrepriseApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='expeditions'
    )

    def clean(self):
        super().clean()
        if self.entreprise and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError("L'entreprise doit être de type chargeur.")

    def save(self, *args, **kwargs):
        if not self.reference:
            annee = timezone.now().strftime('%y')
            prefix = f"EXP-{annee}"
            count = Expedition.objects.filter(reference__startswith=prefix).count() + 1
            self.reference = f"{prefix}-{count:05d}"
        super().save(*args, **kwargs)