# Generated by Django 5.1 on 2024-08-17 13:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0003_alter_loanac_loan_scheme'),
        ('otrans', '0005_withdraw'),
        ('primary_setup', '0017_dpsscheme'),
    ]

    operations = [
        migrations.CreateModel(
            name='Passbook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Account', models.CharField(max_length=200)),
                ('processed_by', models.CharField(blank=True, max_length=50, null=True)),
                ('Date', models.DateField()),
                ('Amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Note', models.CharField(blank=True, max_length=200, null=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='primary_setup.branch')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app1.customer')),
            ],
        ),
    ]
