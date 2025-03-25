from django.urls import path
from django.shortcuts import get_object_or_404
from .models import Weapon
import segno
import io
from django.http import HttpResponse

def print_single_qr_code(request, weapon_id):
    """
    View to print a single QR code from the list view
    """
    weapon = get_object_or_404(Weapon, pk=weapon_id)
    qr = segno.make(weapon.qr_code, error='H')
    buffer = io.BytesIO()
    qr.save(buffer, kind='png', scale=10, dark='#000000', light='#FFFFFF')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{weapon.weapon_id}_qr_code.png"'
    return response
