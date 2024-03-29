from .keys import phonecheck_api_key
import requests
import json
import datetime
import pandas as pd
import math
from .models import (
    deviceAttributes,
    devices,
    purchaseOrders,
    faults,
    BackMarketListing,
    warehouse,
    salesOrders,
    salesOrderItems,
    customer,
    address,
    currencies,
    shipment,
    RefurbedListing,
    AppConfig,
)
from collections import defaultdict
from django.db import IntegrityError
from django.conf import settings
import logging
from django.http import HttpResponse, JsonResponse
from .utils import get_mock
import base64
from google.cloud import storage
import io
from django.db.models import IntegerField, Sum, Count
from django.db.models.functions import Cast

# This script is used to import devices from the PhoneCheck API


class PhoneCheckAPI:
    BASE_URL = "https://clientapiv2.phonecheck.com/cloud/CloudDB"
    INFO = {
        "Apikey": "76d9b060-3417-475c-881c-7403463a0f2e",
        "Username": "elite2",
    }

    @classmethod
    def getAll(cls, date_start=None, date_finish=None, po_number=None):
        td = datetime.datetime.today()
        today = td.strftime("%Y-%m-%d")
        if date_start:
            date = {"startdate": str(date_start), "enddate": today}
            if date_finish:
                date["enddate"] = str(date_finish)
        else:
            date = {"Date": today}
        reqUrl = f"{cls.BASE_URL}/v2/GetAllDevices/"

        headersList = {"Content-Type": "application/json"}

        payload = json.dumps(
            {
                **cls.INFO,
                **date,
                "Invoiceno": po_number,
            }
        )

        response = requests.request(
            "POST", reqUrl, data=payload, headers=headersList
        ).json()
        df = response[1:]

        if response[0]["numOfRecords"] > 500:
            for i in range(math.ceil(response[0]["numOfRecords"] / 500) - 1):
                payload["offset"] = 500 * (i + 1)

                response2 = requests.request(
                    "POST", reqUrl, data=payload, headers=headersList
                ).json()[1]
                newDf = pd.DataFrame(response2[1:])
                df = pd.concat([df, newDf])

        return df

    @classmethod
    def getBulkIMEI(cls, imeis):
        reqUrl = f"{cls.BASE_URL}/getDeviceInfoforBulkIMEI"

        headersList = {"Content-Type": "application/json"}

        payload = json.dumps({**cls.INFO, "IMEI": imeis, "archive_search": 1})
        response = requests.request("POST", reqUrl, data=payload, headers=headersList)

        devicesFromPC = response.json()
        return devicesFromPC

    @classmethod
    def addToDB(cls, devicesToUpload, wh="Belfast"):

        missing_sku_details = defaultdict(list)
        missing_po = []
        uploaded = []
        duplicate_devices = []
        for imei in devicesToUpload:
            device = devicesToUpload[imei]
            # Attempt to fetch the PO instance
            po_instance = None
            whInstance, created = warehouse.objects.get_or_create(name=wh)
            try:
                po_instance = purchaseOrders.objects.get(po=device["InvoiceNo"])
            except purchaseOrders.DoesNotExist:
                missing_po.append(device)
                po_instance = purchaseOrders(id=1)
            try:
                sku_instance = calculateSKU(device)
            except ValueError as e:
                print(e)
                # Extract attributes
                model = device.get("Model")
                capacity = device.get("Memory")
                color = device.get("Color")
                grade = device.get("Grade")

                # Increment count in the dictionary
                missing_sku_details[(model, capacity, color, grade)].append(
                    {imei: device}
                )

                continue
            try:
                new_device = devices(
                    imei=device["IMEI"],
                    sku=sku_instance,
                    deviceStatus_id=2 if device["Working"] == "Yes" else 1,
                    battery=device["BatteryHealthPercentage"].replace("%", ""),
                    date_tested=datetime.datetime.strptime(
                        device["CreatedTimeStamp"].split("T")[0], "%Y-%m-%d"
                    ),
                    working=(
                        True
                        if device["Working"] == "Yes"
                        else False if device["Working"] == "No" else None
                    ),
                    po=po_instance,
                    warehouse=whInstance,
                )
                new_device.save()
                if device["Failed"]:
                    if len(device["Failed"]) > 1:
                        for fault_description in device["Failed"]:
                            fault = faults(device=new_device, fault=fault_description)
                            fault.save()
                    else:
                        fault = faults(device=new_device, fault=fault_description)
                        fault.save()

                uploaded.append(imei)

            except IntegrityError as e:
                duplicate_devices.append(imei)

            except Exception as e:
                print(e)

        grouped_missing_skus = [
            {
                "missing_id": key[0].replace(" ", "") + str(i),
                "model": key[0],
                "capacity": key[1],
                "color": key[2],
                "grade": key[3],
                "count": len(devices),
                "devices": devices,
            }
            for i, (key, devices) in enumerate(missing_sku_details.items())
        ]

        return uploaded, grouped_missing_skus, missing_po, duplicate_devices


class BackMarketAPI:
    BASE_URL = (
        "https://preprod.backmarket.co.uk/ws"
        if settings.BM_PREPROD
        else "https://www.backmarket.co.uk/ws"
    )
    API_KEY = (
        settings.APIKEYS["BM_PRE"] if settings.BM_PREPROD else settings.APIKEYS["BM"]
    )
    HEADERS = {
        "Accept-Language": "en-gb",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": API_KEY,
    }

    @classmethod
    def get_listings(cls, publication_state=2, start=0, page_length=50):
        BackMarketListing.objects.all().update(quantity=0)
        results = []
        skus_to_fetch = []
        # Fetch listings in batches and collect skus to fetch in a single query
        next = f"{cls.BASE_URL}/listings"
        querystring = {
            "page": 1,  # Reset page for each batch
            "page-size": 50,
            "publication_state": publication_state,
        }
        while True:
            response = requests.get(
                next, headers=cls.HEADERS, params=querystring
            ).json()
            results.extend(response["results"])
            skus_to_fetch.extend(
                listing["sku"]
                for listing in response["results"]
                if "IP" in listing["sku"]
            )
            next = response.get("next", None)
            querystring = {}
            if not next:
                break

        # Fetch skus in a single query
        sku_mapping = {}
        if skus_to_fetch:
            sku_objects = deviceAttributes.objects.filter(
                sku__in=skus_to_fetch
            ).in_bulk()  # Use in_bulk for efficient lookup
            sku_mapping = {obj.sku: obj for _, obj in sku_objects.items()}

        items = []
        for listing in results:
            if "IP" not in listing["sku"]:
                continue
            sku = listing["sku"]
            sku_obj = sku_mapping.get(sku)

            # Create or update BackMarketListing instance
            instance, created = BackMarketListing.objects.update_or_create(
                listing_id=listing["listing_id"],
                defaults={
                    "sku": sku_obj,  # Use fetched sku object if available
                    "bm_sku": listing["sku"],
                    "title": listing["title"],
                    "price": listing["price"],
                    "min_price": listing["min_price"],
                    "quantity": listing["quantity"],
                    "backmarket_id": listing["backmarket_id"],
                    "product_id": listing["product_id"],
                    "max_price": listing["max_price"],
                },
            )
            items.append(instance)
        manage_stock = AppConfig.get_value("manage_stock", "false") == "true"
        if manage_stock:
            for listing in items:
                available_stock = calculate_available_stock()
                try:
                    sku = listing.sku.sku
                    if listing.quantity > available_stock.get(listing.sku.sku, 0):
                        cls.update_listing(
                            listing.listing_id, available_stock.get(listing.sku.sku, 0)
                        )
                        listing.quantity = available_stock.get(listing.sku.sku, 0)
                        listing.save()
                except:
                    pass
        total = len(items)
        return items, total

    @classmethod
    def get_listing_by_id(cls, id, marketplace):
        url = f"{cls.BASE_URL}/listings/{id}"
        headers = {
            **cls.HEADERS,
            "Accept-Language": marketplace,
        }
        response = requests.get(url, headers=headers).json()
        return response

    @classmethod
    def update_listing(cls, listing_id, quantity):
        url = f"{cls.BASE_URL}/listings/{listing_id}"
        headers = {
            **cls.HEADERS,
            "Accept-Language": "en-gb",
        }
        data = {"quantity": quantity}
        response = requests.post(url, headers=headers, json=data).json()
        return response

    @classmethod
    def get_orders(cls, state=1):

        # Get Orders from BM (default get pending orders)
        headers = {
            **cls.HEADERS,
            "Accept-Language": "en-gb",
        }
        params = {
            "state": state,
            "page-size": "50",
            "date_creation": "2023-01-01 12:00:00",
        }

        response = requests.request(
            "GET", f"{cls.BASE_URL}/orders", headers=headers, params=params
        ).json()
        if response["count"] < 50:
            results = response["results"]
        else:
            responseJoin = []
            pagecount = response["count"] // 50 + 1
            for i in range(1, pagecount + 1):
                reqUrl = f"{cls.BASE_URL}/orders&page={i}"
                response = requests.request("GET", reqUrl, headers=headers).json()[
                    "results"
                ]
                responseJoin += response
            results = responseJoin
        # Process each order
        for order in results:
            if salesOrders.objects.filter(so=order["order_id"]).exists():
                continue
            # Get or Create Shipping Address
            phone = (
                order["shipping_address"]["phone"]
                if order["shipping_address"]["phone"]
                else "N/A"
            )
            shipping_address, _ = address.objects.get_or_create(
                name=order["shipping_address"]["first_name"]
                + " "
                + order["shipping_address"]["last_name"],
                street=order["shipping_address"]["street"],
                street2=order["shipping_address"]["street2"],
                city=order["shipping_address"]["city"],
                # state=order["shipping_address"]["state"],
                postalCode=order["shipping_address"]["postal_code"],
                phone=phone,
                country=order["shipping_address"]["country"],
            )

            # Get or Create Billing Address (assuming it's different from shipping)
            billing_address, _ = address.objects.get_or_create(
                name=order["billing_address"]["first_name"]
                + " "
                + order["billing_address"]["last_name"],
                street=order["billing_address"]["street"],
                street2=order["billing_address"]["street2"],
                city=order["billing_address"]["city"],
                # state=order["billing_address"]["state"],
                postalCode=order["billing_address"]["postal_code"],
                phone=phone,
                country=order["shipping_address"]["country"],
            )

            # Get or Create Customer
            customer_obj, _ = customer.objects.get_or_create(
                name=order["shipping_address"]["first_name"]
                + " "
                + order["shipping_address"]["last_name"],
                shipping_address=shipping_address,
                billing_address=billing_address,
                email=order["shipping_address"]["email"],
                company=order["shipping_address"]["company"],
                defaults={
                    "contact": order["billing_address"]["first_name"]
                    + " "
                    + order["billing_address"]["last_name"],
                    "email": "",  # Not available in the API
                    "channel": "BackMarket",
                    "currency": currencies.objects.get(
                        name=order["orderlines"][0]["currency"]
                    ),
                },
                # currency and channel might be added here if available
            )

            # Create Sales Order
            sales_order, _ = salesOrders.objects.get_or_create(
                so=order["order_id"],
                defaults={
                    "customer": customer_obj,
                },
            )

            for orderline in order["orderlines"]:
                # Create Sales Order Items
                try:
                    sku = deviceAttributes.objects.get(sku=orderline["listing"])
                except deviceAttributes.DoesNotExist:
                    sku = orderline["listing"]
                salesOrderItem = salesOrderItems.objects.create(
                    salesorder=sales_order,
                    description=orderline["product"],
                    sku=sku,  # Assuming this is a correct reference to a deviceAttributes object
                    quantity=orderline["quantity"],
                    unit_cost=float(orderline["price"]),  # Convert to float
                )
                # # # Confirm Line Item
                confirm_url = f"{cls.BASE_URL}/orders/{salesOrderItem.salesorder.so}"
                payload = json.dumps(
                    {
                        "order_id": salesOrderItem.salesorder.so,
                        "new_state": 2,
                        "sku": salesOrderItem.sku.sku,
                    }
                )
                response = requests.post(confirm_url, data=payload, headers=headers)
                if response.status_code == 200:
                    sales_order.state = "Confirmed"
                    sales_order.save()
                else:
                    sales_order.state = "Unconfirmed"
                    sales_order.save()

    @classmethod
    def update_orders(cls, so):
        sales_order = salesOrders.objects.prefetch_related("devices", "shipment").get(
            pk=so
        )
        shipment = sales_order.shipment.all()[0]
        shippedDevices = sales_order.devices.all()
        order_id = sales_order.so
        url = f"{cls.BASE_URL}/orders/{order_id}"
        for device in shippedDevices:
            body = {
                "order_id": order_id,
                "new_state": 3,
                "sku": device.sku.sku,
                "imei": device.imei if len(shippedDevices) == 1 else None,
                "tracking_number": shipment.tracking_number,
                "tracking_url": shipment.tracking_url,
                "vat_type": "MARGINAL",
                "date_shipping": f"{shipment.date_shipped.strftime('%Y-%m-%d')} 12:00:00",
                "shipper": shipment.shipper,
            }
            response = requests.post(url, json=body, headers=cls.HEADERS)
        sales_order.state = "Shipped"
        sales_order.save()

    @classmethod
    def sync_stock(cls):
        listed = BackMarketListing.objects.filter(quantity__gte=0)
        available = calculate_available_stock()


class DHLAPI:
    BASE_URL = "https://express.api.dhl.com/mydhlapi"
    HEADERS = {
        "Authorization": f"Basic {settings.APIKEYS['DHL']}",
    }

    @classmethod
    def get_available_shipping(cls, customerid):

        address = customer.objects.get(pk=customerid).shipping_address
        data = {
            "accountNumber": "425992913",
            "originCountryCode": "GB",
            "originPostalCode": "BT2 7BG",
            "originCityName": "Belfast",
            "destinationCountryCode": address.country,
            "destinationPostalCode": address.postalCode,
            "destinationCityName": address.city,
            "weight": "0.5",
            "length": "15",
            "width": "10",
            "height": "5",
            # "plannedShippingDate": "2024-02-09",
            "plannedShippingDate": datetime.datetime.now().date().strftime("%Y-%m-%d"),
            "isCustomsDeclarable": "false",
            "unitOfMeasurement": "metric",
        }

        response = requests.get(
            url=f"{cls.BASE_URL}/rates", headers=cls.HEADERS, params=data
        )
        if response.status_code != 200:
            return JsonResponse(
                response.json(), status=response.status_code, safe=False
            )
        services = []
        for product in response.json()["products"]:
            product_name = product.get("productName", "N/A")
            product_code = product.get("productCode", "N/A")
            weight_provided = product.get("weight", {}).get("provided", "N/A")
            total_prices = product.get("totalPrice", [])
            est_delivery = product["deliveryCapabilities"].get(
                "estimatedDeliveryDateAndTime", "N/A"
            )
            if total_prices == []:
                continue
            # Prices in GBP and EUR
            for price in total_prices:
                if price.get("priceCurrency") == "GBP":
                    price_gbp = price.get("price", "N/A")
                elif price.get("priceCurrency") == "EUR":
                    price_eur = price.get("price", "N/A")

            services.append(
                {
                    "Name": product_name,
                    "Code": product_code,
                    "Weight": weight_provided,
                    "gbPrice": price_gbp,
                    "euPrice": price_eur,
                    "est_delivery": est_delivery.split("T")[0],
                }
            )

        sorted_services = sorted(services, key=lambda x: x["gbPrice"])
        return JsonResponse({"services": sorted_services}, status=200)

    @classmethod
    def buy_shipping_label(cls, customerid, shipping_service, so):
        # Check if there is already a label:
        if shipment.objects.filter(so_id=so).exists():
            shipment.objects.filter(so_id=so).delete()
        customer_instance = customer.objects.get(pk=customerid)

        ship_to_address = customer_instance.shipping_address
        body = {
            "valueAddedServices": [{"serviceCode": "PT"}],
            "productCode": shipping_service,
            "customerReferences": [{"value": "Customer reference", "typeCode": "CU"}],
            "plannedShippingDateAndTime": f"{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')} GMT+01:00",
            "pickup": {"isRequested": False},
            "outputImageProperties": {
                "encodingFormat": "pdf",
                "imageOptions": [
                    {
                        "templateName": "COMMERCIAL_INVOICE_P_10",
                        "invoiceType": "commercial",
                        "isRequested": False,
                        "typeCode": "invoice",
                    }
                ],
            },
            "accounts": [{"number": "425992913", "typeCode": "shipper"}],
            "customerDetails": {
                "receiverDetails": {
                    "postalAddress": {
                        "cityName": ship_to_address.city,
                        "countryCode": ship_to_address.country,
                        "postalCode": ship_to_address.postalCode,
                        "addressLine1": ship_to_address.street,
                    },
                    "contactInformation": {
                        "phone": "07863679649",
                        "companyName": (
                            customer_instance.company
                            if customer_instance.company
                            else ship_to_address.name
                        ),
                        "fullName": ship_to_address.name,
                        "email": (
                            customer_instance.email
                            if customer_instance.email
                            else "david@eliteinnovations.co.uk"
                        ),
                    },
                    "registrationNumbers": [
                        {
                            "number": "GB12345",
                            "issuerCountryCode": "GB",
                            "typeCode": "VAT",
                        },
                        {
                            "number": "GB12345",
                            "issuerCountryCode": "GB",
                            "typeCode": "EOR",
                        },
                    ],
                    "typeCode": "business",
                },
                "shipperDetails": {
                    "postalAddress": {
                        "cityName": "Belfast",
                        "countryCode": "GB",
                        "postalCode": "BT2 7BG",
                        "addressLine1": "128a Great Victoria St",
                    },
                    "contactInformation": {
                        "phone": "1212345678",
                        "companyName": "We Sell Mobiles",
                        "fullName": "Chris Seiffert",
                        "email": "chris.seiffert@eliteinnovations.co.uk",
                    },
                    "typeCode": "business",
                },
            },
            "content": {
                "exportDeclaration": {
                    "lineItems": [
                        {
                            "number": 1,
                            "commodityCodes": [
                                {"value": "HS1234567890", "typeCode": "outbound"}
                            ],
                            "priceCurrency": "GBP",
                            "quantity": {"unitOfMeasurement": "BOX", "value": 1},
                            "price": 150,
                            "description": "line item description",
                            "weight": {"netValue": 10, "grossValue": 10},
                            "exportReasonType": "permanent",
                            "manufacturerCountry": "CZ",
                        }
                    ],
                    "exportReason": "Sale",
                    "additionalCharges": [{"value": 10, "typeCode": "freight"}],
                    "invoice": {
                        "date": "2020-03-18",
                        "number": "12345-ABC",
                        "signatureName": "Brewer",
                        "signatureTitle": "Mr.",
                    },
                    "shipmentType": "commercial",
                },
                "unitOfMeasurement": "metric",
                "isCustomsDeclarable": False,
                "incoterm": "DAP",
                "description": "shipment description",
                "packages": [
                    {
                        "customerReferences": [
                            {"value": "Piece reference", "typeCode": "CU"}
                        ],
                        "weight": 0.5,
                        "description": "Used Mobile Device (RETAIL)",
                        "dimensions": {"length": 20, "width": 10, "height": 5},
                    }
                ],
                "declaredValueCurrency": "GBP",
                "declaredValue": 150,
            },
        }
        response = requests.post(
            url="https://express.api.dhl.com/mydhlapi/shipments",
            headers=cls.HEADERS,
            json=body,
        ).json()
        # mock_response = get_mock()
        tracking_number = response["shipmentTrackingNumber"]
        tracking_url = response["trackingUrl"]
        public_tracking_url = "N/A"  # This needs calculating
        label = response["documents"][0]["content"]

        # Upload the label to GCP
        pdf_content = base64.b64decode(label)

        # Initialize Google Cloud Storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket("elite-inn-inventory.appspot.com")

        # Create a new blob and upload the PDF's content
        blob = bucket.blob(f"{customer_instance.name}_{tracking_number}.pdf")
        blob.upload_from_string(pdf_content, content_type="application/pdf")
        label_url = blob.public_url
        shipment_instance = shipment(
            date_shipped=datetime.datetime.now().strftime("%Y-%m-%d"),
            so_id=so,
            tracking_number=tracking_number,
            tracking_url=tracking_url,
            public_tracking_url=label_url,
            label_blob_name=blob.name,
        ).save()

        return HttpResponse(label, status=200)


class GCPAPI:

    BUCKET_NAME = "elite-inn-inventory.appspot.com"

    @classmethod
    def stream_gcs_file(cls, blob_name):

        storage_client = storage.Client()
        bucket = storage_client.bucket(cls.BUCKET_NAME)
        blob = bucket.blob(blob_name)

        # Use a BytesIO buffer to hold the file content
        file_buffer = io.BytesIO()
        # Download the file to the buffer
        blob.download_to_file(file_buffer)
        # Seek to the start of the file
        file_buffer.seek(0)

        return file_buffer


class REFURBEDAPI:
    BASE_URL = "https://api.refurbed.com/refb.merchant.v1."
    HEADERS = {"Authorization": settings.APIKEYS["REFURBED"]}

    @classmethod
    def get_listings(cls):
        body = {"filter": {"stock": {"gt": 0}}}
        url = f"{cls.BASE_URL}OfferService/ListOffers"
        offers = []
        response = requests.post(url, headers=cls.HEADERS, json=body).json()
        offers.extend(response["offers"])
        if response["has_more"]:
            while response["has_more"]:
                last_id = response["offers"][-1]["id"]
                body["pagination"] = {"starting_after": last_id}
                response = requests.post(url, headers=cls.HEADERS, json=body).json()
                offers.extend(response["offers"])
        for listing in offers:
            try:
                sku_instance = deviceAttributes.objects.get(sku=listing["sku"])
            except:
                sku_instance = None

            RefurbedListing.objects.update_or_create(
                listing_id=listing["id"],
                defaults={
                    "title": listing["instance_name"],
                    "sku": sku_instance,
                    "quantity": listing["stock"],
                    "refurbed_sku": listing["sku"],
                    "ref_price": listing["reference_price"],
                },
            )
        return response

    @classmethod
    def get_orders(cls):
        url = f"{cls.BASE_URL}OrderService/ListOrders"
        body = {"filter": {"state": {"any_of": "ACCEPTED"}}}
        response = requests.post(url, headers=cls.HEADERS, json=body).json()
        for order in response["orders"]:
            shipping_address, _ = address.objects.get_or_create(
                name=f"{order['shipping_address']['first_name']} {order['shipping_address']['family_name']}",
                street=order["shipping_address"]["street_name"],
                street2=order["shipping_address"].get("house_no"),
                city=order["shipping_address"]["town"],
                state="",  # State is not provided in the JSON
                postalCode=order["shipping_address"]["post_code"],
                phone=order["shipping_address"]["phone_number"],
                country=order["shipping_address"]["country_code"],
            )

            # Assuming billing_address is the same as shipping_address in this scenario
            billing_address, _ = address.objects.get_or_create(
                name=f"{order['invoice_address']['first_name']} {order['invoice_address']['family_name']}",
                street2=order["invoice_address"]["street_name"],
                street=order["invoice_address"].get("house_no"),
                city=order["invoice_address"]["town"],
                state="",  # State is not provided in the JSON
                postalCode=order["invoice_address"]["post_code"],
                phone=order["invoice_address"]["phone_number"],
                country=order["invoice_address"]["country_code"],
            )

            # Process Customer
            currency = currencies.objects.get(name=order["currency_code"])
            customer_instance, _ = customer.objects.update_or_create(
                email=order["customer_email"],
                defaults={
                    "name": f"{order['shipping_address']['first_name']} {order['shipping_address']['family_name']}",
                    "shipping_address": shipping_address,
                    "billing_address": billing_address,
                    "contact": order["shipping_address"]["phone_number"],
                    "phone": order["shipping_address"]["phone_number"],
                    "currency": currency,
                    # Assuming the channel or company might be part of a larger context not provided in the JSON
                    # 'company': 'Your logic here',
                    "channel": "Refurbed",
                },
            )

            # Process Sales Order
            sales_order, _ = salesOrders.objects.update_or_create(
                so=order["id"],
                defaults={
                    "customer": customer_instance,
                    "state": "Confirmed",
                    # Fields like 'shipped_by' and 'warehouse' would need additional context or logic
                },
            )

            # Assuming you might also want to process items in the order
            for item in order["items"]:
                sku_instance = deviceAttributes.objects.get(sku=item["sku"])
                sales_order_item, _ = salesOrderItems.objects.update_or_create(
                    salesorder=sales_order,
                    sku=sku_instance,  # This assumes 'sku' can directly relate to your deviceAttributes model.
                    defaults={
                        "description": item["name"],
                        "quantity": 1,  # Quantity is not directly provided; assuming 1 or extract as needed
                        "unit_cost": item["total_charged"],
                    },
                )

        return response

    @classmethod
    def update_listing(cls, listing_id, quantity):
        url = f"{cls.BASE_URL}OfferService/UpdateOffer"
        body = {"identifier": {"id": listing_id}, "stock": quantity}
        response = requests.post(url, headers=cls.HEADERS, json=body).json()
        return response


def calculateSKU(phoneData):
    model = phoneData["Model"]
    colour = phoneData["Color"]
    capacity = phoneData["Memory"]
    grade = phoneData["Grade"]

    # Use filter to find a matching deviceAttributed record
    matching_records = deviceAttributes.objects.filter(
        model__iexact=model, color=colour, capacity=capacity, grade=grade
    )

    # Check if a matching record was found
    if matching_records.exists():
        SKU = matching_records.first()  # Get the first matching record
        return SKU
    else:
        raise ValueError("No matching SKU found")


def getWCResults():
    reqUrl = "https://api.wholecell.io/api/v1/inventories/?status=Moving&location=Main%20N.I%20Warehouse"

    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Authorization": "Basic dTZSUkY0RmRmaUh5Vl9OcXRHbVFOUTU5MUdsNGVfVHN2NmZmR3FaUUV1M3c6WEZMU05rWDlXRTlzZkhVbnBSbFpvd1cxOW1BTUIyMnktRHo1X2lmWnZtd0E",
    }

    payload = ""

    phones = requests.request("GET", reqUrl, data=payload, headers=headersList).json()[
        "data"
    ]
    ids = [phone["id"] for phone in phones]
    imeis = [phone["esn"] for phone in phones]
    phonestoadd = []
    missingSKUs = []

    for phone in phones:
        try:
            toadd = devices(
                imei=phone["esn"],
                sku=calculateSKU(
                    {
                        "Model": phone["product_variation"]["product"]["model"],
                        "Color": phone["product_variation"]["product"]["color"],
                        "Memory": phone["product_variation"]["product"]["capacity"],
                        "Grade": phone["product_variation"]["grade"],
                    }
                ),
                deviceStatus_id=2,
            )
            phonestoadd.append(toadd)
        except:
            missingSKUs.append(phone)
            continue

    return phonestoadd, missingSKUs


def bulkUploadPhones(df, warehouse):
    missing_sku_details = defaultdict(list)
    missing_po = []
    uploaded = []
    duplicate_devices = []

    for device in df:
        # Attempt to fetch the PO instance
        po_instance = None
        try:
            po_instance = purchaseOrders.objects.get(po=device["InvoiceNo"])
        except purchaseOrders.DoesNotExist:
            missing_po.append(device)
        try:
            sku_instance = calculateSKU(device)
        except ValueError as e:
            print(e)
            # Extract attributes
            model = device.get("Model")
            capacity = device.get("Memory")
            color = device.get("Color")
            grade = device.get("Grade")

            # Increment count in the dictionary
            missing_sku_details[(model, capacity, color, grade)].append(device)

            continue

        try:
            new_device = devices(
                imei=device["IMEI"],
                sku=sku_instance,
                deviceStatus_id=3 if device["Working"] == "Yes" else 2,
                battery=device["BatteryHealthPercentage"],
                date_tested=datetime.datetime.strptime(
                    device["CreatedTimeStamp"].split("T")[0], "%Y-%m-%d"
                ),
                working=(
                    True
                    if device["Working"] == "Yes"
                    else False if device["Working"] == "No" else None
                ),
                po=po_instance,
                warehouse_id=warehouse,
            )
            new_device.save()
            if device["Failed"]:
                for fault_description in device["Failed"]:
                    fault = faults(device=new_device, fault=fault_description)
                    fault.save()
            uploaded.append(device["IMEI"])

        except IntegrityError as e:
            duplicate_devices.append(device["IMEI"])

        except Exception as e:
            print(e)

        grouped_missing_skus = [
            {
                "model": key[0],
                "capacity": key[1],
                "color": key[2],
                "grade": key[3],
                "count": len(devices),
                "devices": devices,
            }
            for key, devices in missing_sku_details.items()
        ]


def calculate_available_stock(battery=84, grades=["A", "A/B", "B/C"]):
    groupedStock = (
        devices.objects.filter(
            deviceStatus=2, battery__gte=battery, sku__grade__in=grades
        )
        .values("sku__sku")
        .annotate(count=Count("sku"))
    )
    allocated_stock = (
        salesOrderItems.objects.filter(salesorder__state="Confirmed")
        .values("sku__sku")
        .annotate(count=Sum("quantity"))
    )
    groupedStockDict = {item["sku__sku"]: item["count"] for item in groupedStock}
    allocatedStockDict = {item["sku__sku"]: item["count"] for item in allocated_stock}

    for sku, count in allocatedStockDict.items():
        if sku in groupedStockDict:
            # Subtract allocated stock from grouped stock, ensuring we don't go below zero
            groupedStockDict[sku] = max(groupedStockDict[sku] - count, 0)

    return groupedStockDict
