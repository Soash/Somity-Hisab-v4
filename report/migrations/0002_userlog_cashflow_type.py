# Generated by Django 5.1 on 2024-08-30 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlog',
            name='cashflow_type',
            field=models.CharField(choices=[('income', 'Income'), ('expense', 'Expense')], default=1, max_length=10),
            preserve_default=False,
        ),
    ]
