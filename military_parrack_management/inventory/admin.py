from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Weapon, Personnel
import re
from django.utils.html import mark_safe
import segno
import io
import base64
import uuid
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
import sys

@admin.register(Weapon)
class WeaponAdmin(ModelAdmin):
    list_display = ('weapon_id', 'status', 'owner_id', 'display_qr_code')
    fields = ('weapon_id', 'bolt_id', 'bolt_carrier_id', 'case_id', 'owner_id')

    # Сонгогдсон зэвсгүүдийг хэвлэх action
    actions = ['bulk_print_qr_codes']

    def save_model(self, request, obj, form, change):
        if not re.match(r'^[A-Z]{2}\d{4}$', obj.weapon_id):
            raise ValueError("Галт зэвсгийн дугаар ийм форматаар бичигдэнэ 'XX1234'")

        if Weapon.objects.filter(weapon_id=obj.weapon_id).exists() and not change:
            raise ValueError("Галт зэвсгийн дугаар дахин давтадахгүй")

        if not obj.qr_code:
            unique_id = str(uuid.uuid4())
            obj.qr_code = unique_id

        super().save_model(request, obj, form, change)

    def display_qr_code(self, obj):
        """
        Админ цонхонд боловсруулагдаж үүссэн QR кодыг харуулах
        """
        if not obj.qr_code:
            return "No QR Code"

        # QR кодыг боловсруулах
        qr = segno.make(obj.qr_code, error='H')

        buffer = io.BytesIO()
        qr.save(buffer, kind='png', scale=10, dark='#000000', light='#FFFFFF')

        # base64 лүү хөрвүүлэх
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return mark_safe(f'<img src="data:image/png;base64,{image_base64}" width="100" height="100" />')

    display_qr_code.short_description = 'QR Код'

    def print_single_qr_code(request, weapon_id):
        try:
            # Explicitly check if weapon exists
            try:
                weapon = Weapon.objects.get(weapon_id=weapon_id)
            except Weapon.DoesNotExist:
                print(f"No weapon found with ID: {weapon_id}")
                print("Existing weapon IDs:")
                for w in Weapon.objects.all():
                    print(w.weapon_id)
                return HttpResponseBadRequest(f"No weapon found with ID: {weapon_id}")

            # Explicit checks
            if not weapon.qr_code:
                return HttpResponseBadRequest("No QR code generated for this weapon")

            # Generate QR code with verbose error handling
            try:
                qr = segno.make(weapon.qr_code, error='H')
            except Exception as qr_error:
                print(f"QR Code generation error: {qr_error}")
                return HttpResponseBadRequest(f"QR Code generation failed: {qr_error}")

            # Buffer and response
            buffer = io.BytesIO()
            qr.save(buffer, kind='png', scale=10, dark='#000000', light='#FFFFFF')
            buffer.seek(0)

            response = HttpResponse(buffer, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{weapon.weapon_id}_qr_code.png"'

            return response

        except Exception as e:
            # Catch-all error handling with full traceback
            print(f"Unexpected error: {e}")
            print(f"Traceback: {sys.exc_info()}")
        
    def bulk_print_qr_codes(self, request, queryset):
        # Олноор нь сонгож хэвлэх
        if queryset.count() == 1:
            # For single item, return a single file
            obj = queryset.first()
            qr = segno.make(obj.qr_code, error='H')
            buffer = io.BytesIO()
            qr.save(buffer, kind='png', scale=10, dark='#000000', light='#FFFFFF')
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{obj.weapon_id}_qr_code.png"'
            return response
        else:
            # For multiple items, create a zip file
            import zipfile
            buffer = io.BytesIO()
            
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for obj in queryset:
                    qr = segno.make(obj.qr_code, error='H')
                    qr_buffer = io.BytesIO()
                    qr.save(qr_buffer, kind='png', scale=10, dark='#000000', light='#FFFFFF')
                    qr_buffer.seek(0)
                    zip_file.writestr(f"{obj.weapon_id}_qr_code.png", qr_buffer.getvalue())
            
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="weapon_qr_codes.zip"'
            return response

    bulk_print_qr_codes.short_description = 'Print QR Codes'

@admin.register(Personnel)
class PersonnelAdmin(ModelAdmin):
    list_display = ('personnel_id', 'f_name', 'l_name')