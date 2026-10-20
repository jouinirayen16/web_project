from django.contrib import admin
from django.urls import path

admin.site.site_header = "TransConnect Administration"
admin.site.site_title = "TransConnect Admin Portal"
admin.site.index_title = "Pilotage Opérationnel des Transports & Expéditions"

urlpatterns = [
    path('admin/', admin.site.urls),
]
