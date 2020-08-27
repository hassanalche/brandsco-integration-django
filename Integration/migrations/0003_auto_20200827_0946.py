# Generated by Django 3.0.8 on 2020-08-27 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Integration', '0002_variant'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='is_erp_cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orders',
            name='is_erp_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orders',
            name='is_erp_fulfilled',
            field=models.BooleanField(default=False),
        ),
    ]