from datetime import timedelta
from django.contrib import admin
from django.db.models import Count
from django.shortcuts import render
from django.urls import path
from django.utils import timezone

from EntrepriseApp.models import Entreprise
from ExpeditionsApp.models import Expedition
from OffresApp.models import Offre
from VehiculesApp.models import Vehicule

admin.site.site_header = "TransConnect Administration"
admin.site.site_title = "TransConnect Admin Portal"
admin.site.index_title = "Pilotage Opérationnel des Transports & Expéditions"

def health_check_view(request):
    maintenant = timezone.now()
    sept_jours_avant = maintenant - timedelta(days=7)

    offres_orphelines = Offre.objects.filter(
        statut__in=['proposee', 'acceptee']
    ).exclude(
        expedition__statut__in=['publiee', 'attribuee']
    ).select_related('expedition', 'transporteur')

    expeditions_bloquees = Expedition.objects.filter(
        statut='publiee',
        created_at__lt=sept_jours_avant
    )

    transporteurs_sans_flotte = Entreprise.objects.filter(
        type_entreprise='transporteur'
    ).annotate(
        nb_vehicules=Count('vehicules')
    ).filter(
        nb_vehicules=0
    )

    vehicules_incoherents = Vehicule.objects.filter(
        disponible=True,
        offres__statut='acceptee'
    ).distinct().select_related('entreprise')

    doublons_propositions = Offre.objects.filter(
        statut='proposee'
    ).values(
        'expedition__reference', 'transporteur__raison_social'
    ).annotate(
        total=Count('id')
    ).filter(
        total__gt=1
    )

    context = {
        **admin.site.each_context(request),
        'title': "Tableau de bord de contrôle d'intégrité",
        'offres_orphelines': offres_orphelines,
        'expeditions_bloquees': expeditions_bloquees,
        'transporteurs_sans_flotte': transporteurs_sans_flotte,
        'vehicules_incoherents': vehicules_incoherents,
        'doublons_propositions': doublons_propositions,
    }
    return render(request, 'admin/health_check.html', context)

original_get_urls = admin.site.get_urls

def get_admin_urls():
    custom_urls = [
        path('health-check/', admin.site.admin_view(health_check_view), name='health-check'),
    ]
    return custom_urls + original_get_urls()

admin.site.get_urls = get_admin_urls

urlpatterns = [
    path('admin/', admin.site.urls),
]

