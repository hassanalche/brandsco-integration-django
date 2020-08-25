import shopify
from Integration.models import Shop, Orders
from Integration.inventory_sync import InventorySync
import time
import requests


class BusinessLogic(object):

    def order_creation (self, request):
        inv = InventorySync()

        shop: Shop = Shop.objects.get(shopUrl = request.META["HTTP_X_SHOPIFY_SHOP_DOMAIN"])

        shop_url = "https://%s:%s@%s/admin" % (shop.apiKey, shop.apiPassword, shop.shopUrl)

        shopify.ShopifyResource.set_site(shop_url)

        order_id = request.META["HTTP_X_SHOPIFY_ORDER_ID"]

        order = shopify.Order.find(order_id)

        Orders.objects.create(order_name = order.name, erp_status = "created")

        shipping = getattr(order, "shipping_address", "")

        try:
            address1 = order.shipping_address.address1
        except Exception as e:
            print(e)
            address1 = ""
        address1 = address1.replace('"', ' ')
        address1 = address1.replace("'", " ")

        try:
            address2 = order.shipping_address.address2
        except Exception as e:
            print(e)
            address2 = ""
        address2 = address2.replace('"', ' ')
        address2 = address2.replace("'", " ")

        try:
            billing_address1 = order.billing_address.address1
        except Exception as e:
            print(e)
            billing_address1 = ""
        billing_address1 = billing_address1.replace('"', ' ')
        billing_address1 = billing_address1.replace("'", " ")

        try:
            billing_address2 = order.billing_address.address2
        except Exception as e:
            print(e)
            billing_address2 = ""
        billing_address2 = billing_address2.replace('"', ' ')
        billing_address2 = billing_address2.replace("'", " ")

        order_lines = []
        for line in order.line_items:

            for i in range(0, 5):
                try:
                    if i < 3:
                        var = shopify.Variant.find(line.variant_id)
                        discount = var.compare_at_price - line.price
                        break
                    else:
                        discount = 0
                        break
                except Exception as e:
                    time.sleep(1)
                    print(e)
                    i = i + 1
            if order.financial_status == "pending":
                paid = 1
            else:
                paid = 0

            if var.barcode is None:
                barcode = ""
            else:
                barcode = var.barcode
            temp = {
                "Entity_ID": "12346",
                "OrderNumberFromWeb": order.name,
                "OrderDate": order.created_at,
                "Status": "PAID and UNFUFILLED",
                "CustomerEmail": getattr(order, "email", ""),
                "BillingAddress1": billing_address1,
                "BillingAddress2": billing_address2,
                "BillingPostalCode": "",
                "BillingCity": getattr(order.billing_address, "city", ""),
                "BillingCountry_ID": getattr(order.billing_address, "country", ""),
                "BillingRegion": "",
                "BillingTelephone1": getattr(order.billing_address, "phone", ""),
                "BillingFirstName": getattr(order.billing_address, "first_name", ""),
                "BillingLastName": getattr(order.billing_address, "last_name", ""),
                "SameAsShippingAddress": 0,
                "ShippingAddress1": address1,
                "ShippingAddress2": address2,
                "ShippingPostalCode": "",
                "ShippingCity": getattr(shipping, "city", ""),
                "ShippingCountry": getattr(shipping, "country", ""),
                "ShippingRegion": "",
                "ShippingTelephone1": getattr(shipping, "first_name", ""),
                "ShippingFirstName": getattr(shipping, "first_name", ""),
                "ShippingSurname": "",
                "OrderTotalValue": 100,
                "OrderSubTotal": 90,
                "Currency": getattr(order, "currency", ""),
                "PaymentMethod": paid,
                "CreditCard_TranID": "",
                "ShippingandHandlingCharges": 30.00,
                "Code": "AA00000012246",
                "Price": line.price,
                "Quantity": line.quantity,
                "LineDiscount": discount,
                "DiscountName": ""
            }
            order_lines.append(temp)

        erp_body = {
            "ScrollerID": "ESFIDocumentTrade/WebSalesOrder",
            "CommandID": "CreateSalesOrder",
            "ReturnTargetDatasets": False,
            "ReturnScrollerDataset": False,
            "OnlyPrepareTargetDatasets": False,
            "ScrollerDataset": {
                "CSESFILineItem": order_lines
            }
        }

        session_id = "Bearer {}".format(inv.get_session_id())
        url = 'http://86.96.206.210:4488/BrandsWebAPI/api/rpc/ScrollerCommand/'
        header = {
            "Authorization": session_id
        }
        response = requests.post(url = url, headers = header, json = erp_body)

        print(response.status_code)

    def order_cancel (self, request):
        inv = InventorySync()

        shop: Shop = Shop.objects.get(shopUrl = request.META["HTTP_X_SHOPIFY_SHOP_DOMAIN"])

        shop_url = "https://%s:%s@%s/admin" % (shop.apiKey, shop.apiPassword, shop.shopUrl)

        shopify.ShopifyResource.set_site(shop_url)

        order_id = request.META["HTTP_X_SHOPIFY_ORDER_ID"]

        order = shopify.Order.find(order_id)

        o = Orders.objects.get(order_name = order.name)
        o.erp_status = 'fulfilled'
        o.save()

        erp_body = { "ScrollerID": "ESFIDocumentTrade/CancelWEBAPI_Orders", "CommandID": "CancelOrder",
                     "ScrollerDataset": { "ESFILineItem": [ { "OrderNumberFromWeb": order.name, "withrestocking": 0 }]},
                     "ReturnTargetDatasets": False, "ReturnScrollerDataset": False, "OnlyPrepareTargetDatasets": False}

        session_id = "Bearer {}".format(inv.get_session_id())
        url = 'http://86.96.206.210:4488/BrandsWebAPI/api/rpc/ScrollerCommand/'
        header = {
            "Authorization": session_id
        }
        response = requests.post(url = url, headers = header, json = erp_body)

        print(response.status_code)

    def order_fulfill (self, request):
        inv = InventorySync()

        shop: Shop = Shop.objects.get(shopUrl = request.META["HTTP_X_SHOPIFY_SHOP_DOMAIN"])

        shop_url = "https://%s:%s@%s/admin" % (shop.apiKey, shop.apiPassword, shop.shopUrl)

        shopify.ShopifyResource.set_site(shop_url)

        order_id = request.META["HTTP_X_SHOPIFY_ORDER_ID"]

        order = shopify.Order.find(order_id)

        o = Orders.objects.get(order_name = order.name)
        o.erp_status = 'fulfilled'
        o.save()

        erp_body = {"ScrollerID": "ESFIDocumentTrade/OrderStatus", "CommandID": "UpdateStatus", "ScrollerDataset": {
            "ESFIDocumentTrade": [{"OrderWebRefNum": order.name, "Status": "PAID and FULFILLED"}]},
                    "ReturnTargetDatasets": False, "ReturnScrollerDataset": False, "OnlyPrepareTargetDatasets": False}

        session_id = "Bearer {}".format(inv.get_session_id())
        url = 'http://86.96.206.210:4488/BrandsWebAPI/api/rpc/ScrollerCommand/'
        header = {
            "Authorization": session_id
        }
        response = requests.post(url = url, headers = header, json = erp_body)

        print(response.status_code)
