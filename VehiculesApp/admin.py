from django.contrib import admin
from .models import Vehicule

@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'entreprise', 'type_vehicule', 'capacite_kg', 'disponible')
    list_filter = ('disponible', 'type_vehicule', 'created_at')
    search_fields = ('immatriculation', 'entreprise__raison_social')
    list_editable = ('disponible',)
    ordering = ('immatriculation',)
    date_hierarchy = 'created_at'
    list_per_page = 15

    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('entreprise',)
    fieldsets = (
        ('Identification', {
            'fields': ('immatriculation', 'entreprise', 'type_vehicule')
        }),
        ('Caractéristiques & Disponibilité', {
            'fields': ('capacite_kg', 'disponible')
        }),
        ('Dates Système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )