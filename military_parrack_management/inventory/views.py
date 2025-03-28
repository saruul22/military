from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import segno
import io
from .models import Weapon

def print_single_qr_code(request, weapon_id):
    # QR кодыг ширхэгээр нь сонгож хэвлэх

    try:
        weapon = get_object_or_404(Weapon, weapon_id=weapon_id)
        qr = segno.make(weapon.qr_code, error='H')
        buffer = io.BytesIO()
        qr.save(buffer, kind='png', scale=10, dark='#000000', light='#FFFFFF')
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{weapon.weapon_id}_qr_code.png"'
        return response
    
    except Exception as e:
        print(f"Error printing QR code: {e}")
        from django.http import HttpResponseBadRequest
        return HttpResponseBadRequest("Error generating QR code")
