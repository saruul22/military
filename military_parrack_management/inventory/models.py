from django.db import models
from django.contrib.auth.models import User
import segno
import uuid



class Personnel(models.Model):
    personnel_id = models.CharField(max_length=3, primary_key=True, unique=True, null=False)
    f_name = models.CharField(max_length=50, null=False)
    l_name = models.CharField(max_length=50, null=False)

class Weapon(models.Model):
    weapon_id = models.CharField(max_length=6, primary_key=True, unique=True)
    bolt_id = models.CharField(max_length=6, unique=True)
    bolt_carrier_id = models.CharField(max_length=6, unique=True)
    case_id = models.CharField(max_length=6, unique=True)
    owner_id = models.OneToOneField(Personnel, on_delete=models.SET_NULL, null=True, blank=True)
    qr_code = models.CharField(unique=True, max_length=255, null=False, blank=False)
    STATUS_CHOICES = [
        ('IN', ('Checked-in')),
        ('OUT', ('Checked-out')),
    ]
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='IN')

    def save(self, *args, **kwargs):
        # зэвсэг бүртгэгдэх бүрт давтагдашгүй QR код үүсгэх
        if not self.qr_code:
            # галт зэвсгийн дугаарт суурилж QR кодыг үүсгэнэ
            self.qr_code = f"WPN-{self.weapon_id}"
        super().save(*args, **kwargs)

    def generate_qr_code_image(self):
        return segno.make(self.qr_code)

    def __str__(self):
        return self.weapon_id
