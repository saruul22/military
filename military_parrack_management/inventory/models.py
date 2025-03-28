from django.db import models
from django.contrib.auth.models import User
import segno
import uuid



class Personnel(models.Model):
    personnel_id = models.CharField(max_length=3, primary_key=True, unique=True, null=False, verbose_name="Алба хаагчийн дугаар")
    f_name = models.CharField(max_length=50, null=False, verbose_name="Алба хаагчийн нэр")
    l_name = models.CharField(max_length=50, null=False, verbose_name="Алба хаагчийн овог")

class Weapon(models.Model):
    weapon_id = models.CharField(max_length=6, primary_key=True, unique=True, verbose_name="Галт зэвсгийн дугаар")
    bolt_id = models.CharField(max_length=6, unique=True, verbose_name="Замгийн дугаар")
    bolt_carrier_id = models.CharField(max_length=6, unique=True, verbose_name='Замгийн рамын дугаар')
    case_id = models.CharField(max_length=6, unique=True, verbose_name="Хайрцаг ангийн тагны дугаар")
    owner_id = models.OneToOneField(Personnel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Эзэмшигчийн дугаар")
    qr_code = models.CharField(unique=True, max_length=255, null=False, blank=False, verbose_name="QR код")
    STATUS_CHOICES = [
        ('IN', ('Орсон')),
        ('OUT', ('Гарсан')),
    ]
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='IN', verbose_name="Төлөв")

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
