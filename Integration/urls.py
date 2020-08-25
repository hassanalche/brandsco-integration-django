from django.conf.urls import url
from .views import Products, OrdersCreation, OrderCancel, Orderfulfill

urlpatterns = [
    url(r'product', Products.as_view()),
    url(r'order', OrdersCreation.as_view()),
    url(r'order_cancel', OrderCancel.as_view()),
    url(r'order_fulfill', Orderfulfill.as_view()),
]