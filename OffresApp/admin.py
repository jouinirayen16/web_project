from django.contrib import admin
from django.utils.html import format_html
from .models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    # Bloc 1 : Personnalisation de base
    list_display = ('id', 'transporteur', 'expedition', 'prix', 'delai_jours', 'statut_badge', 'statut')
    list_filter = ('statut', 'date_proposition')
    search_fields = ('transporteur__raison_social', 'expedition__reference')
    list_editable = ('statut',)
    ordering = ('-created_at',)
    date_hierarchy = 'date_proposition'
    list_per_page = 20

    # Bloc 2 : Affichage avancé & protection des champs auto
    readonly_fields = ('date_proposition', 'created_at', 'updated_at')
    autocomplete_fields = ('transporteur', 'expedition', 'vehicule')

    fieldsets = (
        ('Contexte', {
            'fields': ('expedition', 'transporteur', 'vehicule')
        }),
        ('Proposition Commerciale', {
            'fields': ('prix', 'delai_jours', 'statut')
        }),
        ('Dates Système', {
            'fields': ('date_proposition', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Bloc 2 : Colonne calculée avec badge HTML coloré
    @admin.display(description="Badge Statut")
    def statut_badge(self, obj):
        colors = {
            'proposee': '#3498db',   # Bleu
            'acceptee': '#2ecc71',   # Vert
            'refusee': '#e74c3c',    # Rouge
            'retiree': '#95a5a6',    # Gris
        }
        color = colors.get(obj.statut, '#7f8c8d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_statut_display()
        )