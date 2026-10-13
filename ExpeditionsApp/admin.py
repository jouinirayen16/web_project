from django.contrib import admin
from django.utils.html import format_html
from .models import Expedition
from OffresApp.models import Offer

# Bloc 3 : Relations imbriquées - Offres en lecture seule sur la fiche expédition
class OfferInline(admin.TabularInline):
    model = Offer
    extra = 0
    can_delete = False
    readonly_fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut', 'date_proposition')
    fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut', 'date_proposition')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    # Bloc 1 : Personnalisation de base
    list_display = ('reference', 'entreprise', 'ville_depart', 'ville_arrive', 'statut_badge', 'statut', 'date_souhaitee')
    list_filter = ('statut', 'ville_depart')
    search_fields = ('reference', 'entreprise__raison_social')  # Requis pour autocomplete dans OfferAdmin
    list_editable = ('statut',)
    ordering = ('-created_at',)
    date_hierarchy = 'date_souhaitee'
    list_per_page = 25

    # Bloc 2 : Affichage avancé & protection des champs auto
    readonly_fields = ('reference', 'created_at', 'updated_at')
    autocomplete_fields = ('entreprise',)
    fieldsets = (
        ("Détails de l'expédition", {
            'fields': ('reference', 'entreprise', 'description')
        }),
        ('Trajet et Planning', {
            'fields': ('ville_depart', 'ville_arrive', 'date_souhaitee', 'poids_kg', 'statut')
        }),
        ('Dates Système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Bloc 3 : Relations imbriquées
    inlines = [OfferInline]

    # Bloc 2 : Colonne calculée avec badge HTML coloré
    @admin.display(description="Badge Statut")
    def statut_badge(self, obj):
        colors = {
            'publiee': '#3498db',    # Bleu
            'attribuee': '#f39c12',  # Orange
            'en_cours': '#9b59b6',   # Violet
            'livree': '#2ecc71',     # Vert
            'annulee': '#e74c3c',    # Rouge
        }
        color = colors.get(obj.statut, '#7f8c8d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_statut_display()
        )

    # Bloc 4 : Actions personnalisées - Clôturer les expéditions en cours
    @admin.action(description="Clôturer les expéditions sélectionnées")
    def cloturer_expeditions(self, request, queryset):
        expeditions_en_cours = queryset.filter(statut='en_cours')
        nb_cloturees = 0

        for exp in expeditions_en_cours:
            exp.statut = 'livree'
            exp.full_clean()  # Déclenche les validations métier du modèle
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