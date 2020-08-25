
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import datetime
import xlsxwriter
import smtplib
import time
from email import encoders
import pandas as pd





class InventorySync(object):

    def inventorySync(self):
        print("syncing")
        products = self.getAllProductsFromShopify()

        unfullfilled = self.getUnFulFilledInventory()

        df = pd.DataFrame(self.get_products_from_pos())

        del df['Article']
        del df['Description']
        del df['Category']
        del df['Brand']
        del df['Size']
        del df['Color']
        del df['Fit']
        del df['Handle']
        del df['Title']
        del df['TAG']
        del df['RetailPrice']

        print(df)

        columns = ["SKU", "POS QTY", "SHOPIFY UNFULFILLED QTY", "DIFFERENCE", "SHOPIFY OLD INVENTORY",
                   "SHOPIFY NEW INVENTORY", "STATUS"]

        workbook = xlsxwriter.Workbook('./report.xlsx')

        worksheet = workbook.add_worksheet('Report')

        self.setColumns(worksheet, workbook)
        for x in range(len(columns)):
            worksheet.write(0, x, columns[x], self.heading(workbook))

        rows = 1
        locationId = 36925997116
        for product in products:
            print(rows)
            for variant in product["variants"]:
                worksheet.write(rows, 0, variant["barcode"])
                data = df.loc[df['Code'] == variant["barcode"]]
                unfull = unfullfilled.loc[unfullfilled['sku'] == variant["barcode"]]
                if len(unfull) == 0:
                    unfull = 0
                else:
                    unfull = unfull.values[0]
                    unfull = unfull[1]

                if len(data) == 0:
                    worksheet.write(rows, 1, "-")

                    worksheet.write(rows, 2, unfull)
                    worksheet.write(rows, 3, "-")
                    worksheet.write(rows, 4, variant["inventory_quantity"])
                    # worksheet.write(rows, 6, "0")
                    worksheet.write(rows, 5, variant["inventory_quantity"])
                    worksheet.write(rows, 6, "SKU not found in pos, inventory not synced")


                    #This condition will uncomment when they want sku to be synced with zero when not found in candela

                    # if int(variant.inventory_quantity) != 0:
                    #     status,msg = self.inventoryCall(locationId, variant.inventory_item_id, 0)
                    #     if not status:
                    #         worksheet.write(rows, 6, msg)

                elif len(data) == 1:
                    data = data.values[0]

                    worksheet.write(rows, 1, data[1])


                    worksheet.write(rows, 2, unfull)
                    diference = str(int(data[1]) - int(unfull))


                    worksheet.write(rows, 4, variant["inventory_quantity"])
                    worksheet.write(rows, 3, diference)
                    if int(diference) >= 0:
                        worksheet.write(rows, 5, diference)
                        worksheet.write(rows, 6, "Synced")
                        if int(variant["inventory_quantity"]) != int(diference):

                            status,msg = self.inventoryCall(locationId, variant["inventory_item_id"], diference)
                            if not status:
                                worksheet.write(rows, 6, msg)
                    else:
                        worksheet.write(rows, 5, "0")
                        worksheet.write(rows, 6, "Synced With 0")
                        if int(variant["inventory_quantity"]) != 0:
                            status, msg = self.inventoryCall(locationId, variant["inventory_item_id"], 0)
                            if not status:
                                worksheet.write(rows, 6, msg)

                rows = rows + 1
        workbook.close()
        self.sendEmail()

    def get_session_id(self):
        url = "http://86.96.206.210:4488/BrandsWebAPI/api/login/"
        body = {
                    "SubscriptionID": "SubBrands",
                    "SubscriptionPassword": "passx",
                    "BridgeID": "BrandsMB",
                    "Model": {
                        "UserID": "eswebapi",
                        "Password": "BrAdmin@2020",
                        "BranchID": "001",
                        "LangID": "en-US"
                    }
                }
        response = requests.post(url = url, json = body)
        return response.json()["Model"]["WebApiToken"]

    def inventoryCall(self, locationId, inventoryId, qty):
        i = 0
        while True:
            try:
                if i < 3:

                    base_url = self.connectionToShopify()
                    shop_url = base_url + "/api/2020-04/inventory_levels/set.json"
                    response = requests.post(shop_url, json = {
                        "location_id": locationId,
                        "inventory_item_id": inventoryId,
                        "available": qty
                    })
                    if response.status_code == 200:
                        return True, ""
                    elif response.status_code == 429:
                        i = i + 1
                        time.sleep(1)
                else:
                    return False, "Not synced, Tried 3 times"
                    break
            except Exception as e:
                print("call")
                i = i + 1
                time.sleep(1)
                print(e)

    def getUnFulFilledInventory(self):
        # SyncLogs.objects.create(log="getting Un fulfilled")
        base_url = self.connectionToShopify()

        unfullfilled = []
        cursor = ""
        page = 1
        while True:
            print("orders")
            print(page)
            page = page + 1
            if cursor == "":
                shop_url = base_url + "/api/2020-01/orders.json?limit=250&fulfillment_status=unshipped"
            else:
                shop_url = base_url + "/api/2020-01/orders.json?limit=250&page_info={}".format(cursor)

            print(shop_url)

            order = requests.get(shop_url)
            if order.status_code == 200:
                page_info = order.links
                data = order.json()
                # print(data)
                for obj in data["orders"]:
                    for lineItem in obj["line_items"]:
                        for x in range(lineItem["quantity"]):
                            d = {"sku": lineItem["sku"]}
                            unfullfilled.append(d)

                if "next" in page_info:
                    # print(page_info["next"]["url"].split('page_info='))
                    cursor = page_info["next"]["url"].split('page_info=')[1]
                else:
                    print("breaking")
                    break

                print(len(unfullfilled))
            elif order.status_code == 429:
                time.sleep(1)
            else:
                print(order.status_code)

        df = pd.DataFrame(unfullfilled)
        df = df.groupby(['sku']).size().reset_index(name='counts')
        # SyncLogs.objects.create(log="Returning Unfulfilled Inventory")
        print("Returning Unfulfilled Inventory")
        return df

    def connectionToShopify(self):
        API_KEY = "565ffcb09876ff4c997f5c89b67a15f8"
        PASSWORD = "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"
        shop_url = "https://%s:%s@brandsco-fashion.myshopify.com/admin" % (API_KEY, PASSWORD)

        # API_KEY = "056d502c0348f15326d7aa274da521c5"
        # PASSWORD = "c1a5ec767be080af418d7d7d8d55d827"
        # shop_url = "https://%s:%s@limelight-staging1.myshopify.com/admin" % (API_KEY, PASSWORD)

        return shop_url

    def getAllProductsFromShopify(self):
        base_url = self.connectionToShopify()

        products = []
        cursor = ""

        while True:

            shop_url = base_url + "/api/2020-01/products.json?limit=250&page_info={}".format(cursor)
            # print(shop_url)
            # print(shop_url)
            product = requests.get(shop_url)
            if product.status_code == 200:
                page_info = product.links
                data = product.json()
                # print(data)
                products = products + data["products"]
                # print(data["products"][0]["id"])
                if "next" in page_info:
                    # print(page_info["next"]["url"].split('page_info='))
                    cursor = page_info["next"]["url"].split('page_info=')[1]
                else:
                    print("breaking")
                    break

                print(len(products))
            elif product.status_code == 429:
                time.sleep(1)
                print(product.status_code)
            else:
                print(product.status_code)

        print("returning products")
        return products

    def setColumns(self, worksheet, workbook):
        worksheet.set_column(0, 15, 25, self.center(workbook))
        # worksheet.set_column(11, 11, 100, center(workbook))

    def heading(self, workbook):
        bold = workbook.add_format({'bold': True, 'fg_color': 'black', 'font_color': '#FFD700', 'align': 'center',
                                    'valign': 'vcenter', })
        return bold

    def center(self, workbook):
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'font_size': 10, 'text_wrap': True, })
        return center

    def sendEmail(self):
        msg = MIMEMultipart()
        msg['From'] = "erpsystem@brandsco.com"

        msg['To'] = "itd@brandsco.com, alvir@brandsco.com, inventory@brandsco.com, khawaja.tayyab@alchemative.com"
        # msg['To'] = "hassan.sajjad@alchemative.com"

        msg['Date'] = str(datetime.datetime.now().date())
        msg['Subject'] = "Inventory Sync"
        msg.attach(MIMEText("Inventory Sync"))

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open("./report.xlsx", "rb").read())

        encoders.encode_base64(part)

        part.add_header('Content-Disposition', 'attachment; filename="report.xlsx"')
        msg.attach(part)

        # to = ["hassan.sajjad@alchemative.com"]
        to =  ["itd@brandsco.com", "alvir@brandsco.com", "inventory@brandsco.com", "khawaja.tayyab@alchemative.com"]

        smtp = smtplib.SMTP('smtp.office365.com', 587)
        smtp.starttls()

        smtp.login("erpsystem@brandsco.com", "Br@nds#123")
        smtp.sendmail("erpsystem@brandsco.com", to, msg.as_string())
        smtp.quit()

    def get_products_from_pos(self):
        session_id = "Bearer {}".format(self.get_session_id())
        url = 'http://86.96.206.210:4488/BrandsWebAPI/api/rpc/SimpleScroller/ESMMStockItem/WebInventory_WithBalance'
        header = {
            "Authorization": session_id
        }
        response = requests.get(url = url, headers = header)
        print(response.status_code)
        return response.json()["ESFIItem"]


# bl = InventorySync()
# bl.inventorySync()



