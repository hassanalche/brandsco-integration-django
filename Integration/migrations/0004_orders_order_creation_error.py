# Generated by Django 3.0.8 on 2020-08-27 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Integration', '0003_auto_20200827_0946'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='order_creation_error',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]