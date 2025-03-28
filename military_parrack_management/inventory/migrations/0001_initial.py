# Generated by Django 5.1.7 on 2025-03-26 02:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Personnel',
            fields=[
                ('personnel_id', models.CharField(max_length=3, primary_key=True, serialize=False, unique=True)),
                ('f_name', models.CharField(max_length=50)),
                ('l_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Weapon',
            fields=[
                ('weapon_id', models.CharField(max_length=6, primary_key=True, serialize=False, unique=True)),
                ('bolt_id', models.CharField(max_length=6, unique=True)),
                ('bolt_carrier_id', models.CharField(max_length=6, unique=True)),
                ('case_id', models.CharField(max_length=6, unique=True)),
                ('qr_code', models.CharField(max_length=255, unique=True)),
                ('status', models.CharField(choices=[('IN', 'Checked-in'), ('OUT', 'Checked-out')], default='IN', max_length=3)),
                ('owner_id', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.personnel')),
            ],
        ),
    ]
