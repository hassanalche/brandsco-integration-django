from django.shortcuts import render

# Create your views here.
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import requests


class Products(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        url = "https://565ffcb09876ff4c997f5c89b67a15f8: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@" \
              "brandsco-fashion.myshopify.com/admin/api/2020-04/products.json"

        response = requests.post(url, json = request.data)
        data = response.json()
        print(data)
        if response.status_code == 201:
            url = "https://565ffcb09876ff4c997f5c89b67a15f8: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@" \
                  "brandsco-fashion.myshopify.com/admin/api/2020-04/products/" + str(
                data["product"]["id"]) + "/images.json"

            for image in request.data["product"]["images"]:
                body = {
                    "image": {
                        "src": image["url"]

                    }
                }
                requests.post(url, json = body)
            return Response(status = 201)
        else:
            return Response(response.json(), status = response.status_code)

