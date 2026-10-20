from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Offre(models.Model):
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

    def clean(self):
        super().clean()

        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            raise ValidationError({'transporteur': "L'entreprise proposant l'offre doit être de type 'transporteur'."})

        if self.vehicule_id and self.transporteur_id:
            if self.vehicule.entreprise_id != self.transporteur_id:
                raise ValidationError({'vehicule': "Le véhicule associé doit appartenir à l'entreprise transporteur de l'offre."})

        if not self.pk and self.expedition_id:
            if self.expedition.statut != 'publiee':
                raise ValidationError({'expedition': "Une expédition ne peut recevoir de nouvelles offres que si son statut est 'publiee'."})

        if self.statut == 'proposee' and self.transporteur_id and self.expedition_id:
            qs = Offre.objects.filter(
                expedition=self.expedition,
                transporteur=self.transporteur,
                statut='proposee'
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("Une entreprise ne peut pas avoir deux offres au statut 'proposee' actives simultanément sur la même expédition.")

        if not self.pk and self.vehicule_id:
            if not self.vehicule.disponible:
                raise ValidationError({'vehicule': "Un véhicule indisponible ne peut pas être proposé sur une nouvelle offre."})

        if self.vehicule_id and self.expedition_id:
            poids = self.expedition.poids_kg
            type_v = self.vehicule.type_vehicule
            capacite_max_type = {
                'camionnette': 1500,
                'fourgon': 3500,
                'camion_porteur': 19000,
                'semi_remorque': 26000,
            }
            limite_max = capacite_max_type.get(type_v)
            if limite_max and poids > limite_max:
                raise ValidationError({
                    'vehicule': f"Le poids de l'expédition ({poids} kg) dépasse la capacité maximale indicative pour une {type_v} ({limite_max} kg)."
                })
            if poids > self.vehicule.capacite_kg:
                raise ValidationError({
                    'vehicule': f"Le poids de l'expédition ({poids} kg) dépasse la capacité de ce véhicule ({self.vehicule.capacite_kg} kg)."
                })

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_statut = None
        if not is_new:
            old_statut = Offre.objects.filter(pk=self.pk).values_list('statut', flat=True).first()

        super().save(*args, **kwargs)

        if self.statut == 'acceptee' and (is_new or old_statut != 'acceptee'):
            with transaction.atomic():
                if self.expedition.statut != 'attribuee':
                    self.expedition.statut = 'attribuee'
                    self.expedition.save(update_fields=['statut', 'updated_at'])

                Offre.objects.filter(
                    expedition=self.expedition,
                    statut='proposee'
                ).exclude(pk=self.pk).update(statut='refusee')


