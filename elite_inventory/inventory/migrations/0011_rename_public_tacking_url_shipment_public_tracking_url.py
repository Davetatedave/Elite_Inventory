# Generated by Django 3.2.19 on 2024-02-10 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_shipment_public_tacking_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shipment',
            old_name='public_tacking_url',
            new_name='public_tracking_url',
        ),
    ]
