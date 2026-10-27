
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Expedition
from OffresApp.models import Offre


class EnRetardFilter(admin.SimpleListFilter):
    title = 'En retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return [
            ('oui', 'Oui'),
            ('non', 'Non'),
        ]

    def queryset(self, request, queryset):
        expeditions_en_retard = queryset.filter(
            statut='publiee',
            date_souhaitee__lt=timezone.localdate()
        )

        if self.value() == 'oui':
            return expeditions_en_retard

        if self.value() == 'non':
            return queryset.exclude(
                statut='publiee',
                date_souhaitee__lt=timezone.localdate()
            )

        return queryset


class OffreInline(admin.TabularInline):
    model = Offre
    extra = 0
    can_delete = False

    readonly_fields = (
        'transporteur',
        'vehicule',
        'prix',
        'delai_jours',
        'statut',
        'date_proposition',
    )

    fields = (
        'transporteur',
        'vehicule',
        'prix',
        'delai_jours',
        'statut',
        'date_proposition',
    )

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):

    list_display = (
        'reference',
        'entreprise',
        'ville_depart',
        'ville_arrive',
        'statut_badge',
        'statut',
        'date_souhaitee',
    )

    list_filter = (
        'statut',
        'ville_depart',
        EnRetardFilter,
    )

    search_fields = (
        'reference',
        'entreprise__raison_social',
    )

    list_editable = ('statut',)
    ordering = ('-created_at',)
    date_hierarchy = 'date_souhaitee'
    list_per_page = 25

    readonly_fields = (
        'reference',
        'created_at',
        'updated_at',
    )

    autocomplete_fields = ('entreprise',)

    fieldsets = (
        ("Détails de l'expédition", {
            'fields': (
                'reference',
                'entreprise',
                'description',
            )
        }),
        ('Trajet et Planning', {
            'fields': (
                'ville_depart',
                'ville_arrive',
                'date_souhaitee',
                'poids_kg',
                'statut',
            )
        }),
        ('Dates Système', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    inlines = [OffreInline]

    @admin.display(description="Badge Statut")
    def statut_badge(self, obj):
        colors = {
            'publiee': '#3498db',
            'attribuee': '#f39c12',
            'en_cours': '#9b59b6',
            'livree': '#2ecc71',
            'annulee': '#e74c3c',
        }

        color = colors.get(obj.statut, '#7f8c8d')

        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 12px; '
            'font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_statut_display()
        )

    @admin.action(description="Clôturer les expéditions sélectionnées")
    def cloturer_expeditions(self, request, queryset):
        expeditions_en_cours = queryset.filter(statut='en_cours')
        nb_cloturees = 0

        for exp in expeditions_en_cours:
            exp.statut = 'livree'
            exp.full_clean()
            exp.save()
            nb_cloturees += 1

        if nb_cloturees > 0:
            self.message_user(
                request,
                f"{nb_cloturees} expédition(s) clôturée(s) avec succès."
            )
        else:
            self.message_user(
                request,
                "Aucune expédition 'en_cours' sélectionnée parmi votre choix.",
                level='warning'
            )

    actions = [cloturer_expeditions]