import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import Offre

@admin.action(description="Exporter la sélection en CSV")
def exporter_offres_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="offres.csv"'
    writer = csv.writer(response)
    writer.writerow(['reference_expedition', 'transporteur', 'prix', 'statut'])
    for offre in queryset.select_related('expedition', 'transporteur'):
        writer.writerow([offre.expedition.reference, offre.transporteur.raison_social, offre.prix, offre.statut])
    return response

@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ('id', 'transporteur', 'expedition', 'prix', 'delai_jours', 'statut_badge', 'statut')
    list_filter = ('statut', 'date_proposition')
    search_fields = ('transporteur__raison_social', 'expedition__reference')
    list_editable = ('statut',)
    ordering = ('-created_at',)
    date_hierarchy = 'date_proposition'
    list_per_page = 20
    readonly_fields = ('date_proposition', 'created_at', 'updated_at')
    autocomplete_fields = ('transporteur', 'expedition', 'vehicule')
    actions = [exporter_offres_csv]

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

    def get_readonly_fields(self, request, obj=None):
        base = list(self.readonly_fields)
        if obj and obj.statut == 'acceptee':
            return base + ['prix', 'delai_jours']
        return base

    @admin.display(description="Badge Statut")
    def statut_badge(self, obj):
        colors = {
            'proposee': '#3498db',
            'acceptee': '#2ecc71',
            'refusee': '#e74c3c',
            'retiree': '#95a5a6',
        }
        color = colors.get(obj.statut, '#7f8c8d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_statut_display()
        )