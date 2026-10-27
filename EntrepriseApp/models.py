from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone

def validate_gmail(value):
    if not value.endswith('@gmail.com'):
        raise ValidationError("Seuls les emails appartenant au domaine gmail.com sont acceptés")

class Utilisateur(AbstractUser):
    user_id = models.CharField(
        max_length=8,
        editable=False,
        primary_key=True
    )
    email = models.EmailField(unique=True, validators=[validate_gmail])
    role = models.CharField(
        max_length=20,
        choices=[
            ('chargeur', 'chargeur'),
            ('transporteur', 'transporteur'),
            ('administrateur', 'administrateur')
        ],
        default="chargeur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    telephone = models.CharField(max_length=8)

    def save(self, *args, **kwargs):
        if not self.user_id:
            annee = timezone.now().strftime('%y')
            prefix = f"{annee}user"
            count = Utilisateur.objects.filter(user_id__startswith=prefix).count()
            self.user_id = f"{prefix}{count:02d}"
        super().save(*args, **kwargs)


matricule_regex = RegexValidator(
    regex=r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',
    message="Format du matricule fiscal invalide."
)

class Entreprise(models.Model):
    raison_social = models.CharField(max_length=100)
    matricule_fiscal = models.CharField(
        max_length=20,
        unique=True,
        validators=[matricule_regex]
    )
    type_entreprise = models.CharField(
        max_length=15,
        choices=[
            ('chargeur', 'chargeur'),
            ('transporteur', 'transporteur')
        ]
    )
    adresse = models.TextField(
        validators=[MinLengthValidator(20, "L'adresse doit comporter au moins 20 caractères.")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gerant = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='entreprise')

    def __str__(self):
        return f"{self.raison_social} ({self.type_entreprise})"
