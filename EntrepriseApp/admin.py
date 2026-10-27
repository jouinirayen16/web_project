from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Entreprise
from VehiculesApp.models import Vehicule

class VehiculeInline(admin.TabularInline):
    model = Vehicule
    extra = 1
    fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('user_id', 'username', 'email', 'role', 'telephone')
    list_filter = ('role', 'created_at')
    search_fields = ('user_id', 'username', 'email', 'telephone')
    list_editable = ('role',)
    ordering = ('user_id',)
    date_hierarchy = 'created_at'
    list_per_page = 10

    readonly_fields = ('user_id', 'created_at', 'updated_at')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Métier TransConnect', {
            'fields': ('user_id', 'role', 'telephone', 'created_at', 'updated_at')
        }),
    )


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_social', 'matricule_fiscal', 'type_entreprise', 'gerant', 'created_at')
    list_filter = ('type_entreprise', 'created_at')
    search_fields = ('raison_social', 'matricule_fiscal')
    list_editable = ('type_entreprise',)
    ordering = ('raison_social',)
    date_hierarchy = 'created_at'
    list_per_page = 10

    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('gerant',)
    fieldsets = (
        ('Informations Générale', {
            'fields': ('raison_social', 'matricule_fiscal', 'type_entreprise', 'gerant')
        }),
        ('Coordonnées', {
            'fields': ('adresse',)
        }),
        ('Dates Système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [VehiculeInline]
