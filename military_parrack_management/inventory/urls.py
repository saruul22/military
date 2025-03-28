from django.urls import path
from .views import print_single_qr_code

urlpatterns = [
    path('admin/print_qr_code/<str:weapon_id>/', print_single_qr_code, name='print_single_qr_code'),
]
