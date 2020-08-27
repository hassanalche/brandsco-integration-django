from django.db import models

# Create your models here.



class Shop(models.Model):
    id = models.BigAutoField(primary_key=True)
    shopName = models.TextField(max_length=100, blank=True, null=True)
    apiKey = models.TextField(max_length=100, blank=True, null=True)
    apiPassword = models.TextField(max_length=100, blank=True, null=True)
    shopUrl = models.TextField(max_length=100, blank=True, null=True)

class Orders(models.Model):
    order_name = models.TextField(max_length=100, blank=True, null=True)
    fulfillment_status = models.TextField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True, null = True, blank = True)
    updated_at = models.DateTimeField(auto_now = True)
    erp_status = models.TextField(max_length=5000, blank=True, null=True)
    is_erp_created = models.BooleanField(default = False)
    is_erp_cancelled = models.BooleanField(default = False)
    is_erp_fulfilled = models.BooleanField(default = False)
    order_creation_error = models.TextField(blank = True, null = True, max_length = 1000)

class variant(models.Model):
    sku = models.TextField(max_length=100, blank=True, null=True)