# Generated by Django 5.1 on 2025-01-05 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0084_logo_somity_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loancollection',
            name='VoucherID',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
