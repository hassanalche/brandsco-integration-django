from django.conf.urls import url

from .views import Products

urlpatterns = [
    url(r'product', Products.as_view()),
]