# Generated by Django 3.2.19 on 2024-02-08 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_alter_backmarketlisting_sku'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='name',
            field=models.CharField(default='John', max_length=20, verbose_name='Name'),
            preserve_default=False,
        ),
    ]
