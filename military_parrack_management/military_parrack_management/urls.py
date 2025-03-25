from django.contrib import admin
from django.urls import path

from inventory.urls import print_single_qr_code

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/print_qr_code/<int:weapon_id>/', print_single_qr_code, name='print_single_qr_code'),
]
