from django.shortcuts import render
from django.forms.models import model_to_dict
from django.core import serializers
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from .models import (
    trackingDb,
    devices,
    deviceAttributes,
    deviceStatus,
    faults,
    purchaseOrders,
    BackMarketListing,
    salesOrders,
    salesOrderItems,
    customer,
    address,
    shipment,
)
from datetime import datetime, timedelta
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.db.models import Count
from django.http import HttpResponse, JsonResponse, FileResponse, StreamingHttpResponse
from django.template.loader import render_to_string
from .scripts import (
    PhoneCheckAPI as PC,
    calculateSKU,
    BackMarketAPI as BM,
    DHLAPI as DHL,
)
from collections import defaultdict
from django.dispatch import receiver
from django.db.models.signals import post_save
import requests
import json
from django.conf import settings
from .forms import DeviceAttributesForm
from google.cloud import storage
import base64
import io


def index(request):
    # Default date range: last 30 days
    default_end_date = datetime.today().date()
    default_start_date = default_end_date - timedelta(days=30)

    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    start_date = parse_date(start_date_str) if start_date_str else default_start_date
    end_date = parse_date(end_date_str) if end_date_str else default_end_date
    print(start_date, end_date)
    queryset = trackingDb.objects.all()

    if start_date and end_date:
        if start_date > end_date:
            raise ValueError("Start date cannot be greater than end date")
        queryset = queryset.filter(
            date_creation__gte=start_date, date_creation__lte=end_date
        ).order_by("date_creation")

    # Apply grouping logic based on request
    group_status = request.GET.get("grouped", "individual")

    if group_status != "individual":
        print("grouped")
        queryset = (
            queryset.values(group_status)
            .annotate(count=Count(group_status))
            .order_by("-count")
        )

    page = request.GET.get("page", 1)
    paginator = Paginator(queryset, 10)
    table_info = paginator.get_page(page)
    statuses = trackingDb.objects.values_list("Arrival_Status", flat=True).distinct()

    context = {
        "page_title": "Welcome",
        "table": table_info,
        "request": request,
        "statuses": statuses,
        "date": (start_date, end_date),
        "currentpage": page,
    }

    if request.headers.get("HX-Request", "false") == "true":
        template_name = "inv_table_grouped.html" if group_status else "inv_table.html"
        html = render_to_string(template_name, context, request=request)
        return HttpResponse(html)

    return render(request, "index.html", context=context)


def shipping(request):
    data = trackingDb.objects.all()
    columns = [f for f in trackingDb._meta.fields]
    page = request.GET.get("page", 1)
    paginator = Paginator(data, 10)
    table_info = paginator.get_page(page)
    context = {
        "page_title": "Welcome",
        "table_data": table_info,
        "paginator": paginator,
        "columns": columns,
    }

    return render(request, context=context, template_name="shipping.html")


class deviceDetail(DetailView):
    model = devices
    template_name = "trackingdb_detail.html"


def phoneCheck(request):
    start = request.GET.get("pCStart", None)
    end = request.GET.get("pCEnd", None)
    po = request.GET.get("po", None)
    warehouse = request.GET.get("warehouse", "Belfast")
    df = PC.getAll(start, end, po)

    uploaded, grouped_missing_skus, missing_po, duplicate_devices = PC.addToDB(
        df, warehouse
    )

    context = {
        "upload": uploaded,
        "missing": grouped_missing_skus,
        "po": missing_po,
        "duplicate": duplicate_devices,
    }

    return render(request, context=context, template_name="upload.html")


def newSKU(request):
    if request.method == "POST":
        model = request.POST.get("model")
        capacity = request.POST.get("capacity")
        color = request.POST.get("color")
        grade = request.POST.get("grade")
        sku = request.POST.get("newSku")
        try:
            new_sku = deviceAttributes(
                model=model, capacity=capacity, color=color, grade=grade, sku=sku
            )
            new_sku.save()
            message = "SKU added successfully."
            return JsonResponse({"NewSKU": sku, "message": message})
        except Exception as e:
            message = "Error adding SKU."
            return JsonResponse({"message": message, "error": str(e)}, status=500)


class resolveMarketplaceSku(DetailView):
    model = BackMarketListing
    context_object_name = "listing"
    template_name = "resolve_marketplace_sku.html"


def addStock(request):
    return render(request, template_name="add_stock.html")


def inventory(request):
    models = request.GET.get("models", None)

    device_attributes = deviceAttributes.objects.all()
    statuses = deviceStatus.objects.all().exclude(status__in=["Deleted", "Sold"])

    statusesfortable = serializers.serialize("json", statuses)

    if models:
        device_attributes = device_attributes.filter(model=models)

    distinct_values = {
        field.name: set(getattr(obj, field.name) for obj in device_attributes)
        for field in deviceAttributes._meta.fields
    }

    distinct_values["status"] = statuses = [status.status for status in statuses]
    grades = ["A+", "A", "A/B", "B", "B/C", "C", "ABC"]
    grades_json = json.dumps(grades)
    context = {
        "device_attributes": distinct_values,
        "statuses": statusesfortable,
        "grades": grades_json,
    }
    return render(request, context=context, template_name="inventory.html")


def inventoryAjax(request):
    # Extract parameters sent by DataTables
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))  # Default page size

    search_value = request.GET.get("search[value]", None)
    bulk_search_value = request.GET.getlist("bulk_search_value", None)

    # Data filtering and processing logic here

    models = request.GET.getlist("model[]", None)
    capacity = request.GET.getlist("capacity[]", None)
    grades = request.GET.getlist("grade[]", None)
    colors = request.GET.getlist("color[]", None)
    batteryA = request.GET.get("batteryA", None)
    batteryB = request.GET.get("batteryB", None)
    status = request.GET.getlist("status[]", None)
    order = request.GET.get("order[0][column]", None)
    grouping = request.GET.getlist("grouping[]", None)

    if "Deleted" in status or "Sold" in status:
        phones = (
            devices.all_objects.select_related("sku")
            .select_related("deviceStatus")
            .all()
        )
    else:
        phones = (
            devices.objects.select_related("sku").select_related("deviceStatus").all()
        )

        # Pagination parameters
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    if length == -1:
        length = phones.count()

    # Apply additional filtering based on the search query
    if search_value:
        phones = phones.filter(imei__icontains=search_value)

    if bulk_search_value != [""]:
        listofImeis = bulk_search_value[0].splitlines()
        imeiscleaned = [
            item
            for sublist in [i.split(",") for i in listofImeis]
            for item in sublist
            if item != ""
        ]
        print(imeiscleaned)
        phones = phones.filter(imei__in=imeiscleaned)

    if models:
        phones = phones.filter(sku__model__in=models)

    if capacity:
        phones = phones.filter(sku__capacity__in=capacity)

    if colors:
        phones = phones.filter(sku__color__in=colors)

    if grades:
        phones = phones.filter(sku__grade__in=grades)

    if status:
        if "Unknown" in status:
            phones = phones.filter(deviceStatus__status__in=status) | phones.filter(
                deviceStatus__isnull=True
            )

        else:
            phones = phones.filter(deviceStatus__status__in=status)

    if batteryA:
        phones = phones.filter(battery__gte=batteryA)
    if batteryB:
        phones = phones.filter(battery__lte=batteryB)

    if order:
        column_order = request.GET.get(f"columns[{order}][data]", None)
        print(column_order)
        direction = request.GET.get("order[0][dir]", None)

        if direction == "desc":
            print(direction)
            phones = phones.order_by(f"-{column_order}")
        else:
            print(direction)
            phones = phones.order_by(column_order)

    if grouping != []:
        # Apply grouping
        formatted_groupings = [
            f"deviceStatus__status" if group == "status" else f"sku__{group}"
            for group in grouping
        ]
        print(formatted_groupings)
        phones = (
            phones.values(*formatted_groupings)
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Creating response data
        data = []
        for phone in phones[start : start + length]:
            data_entry = {}
            for formatted_group in formatted_groupings:
                # Splitting the formatted group name to get the original name
                original_group = formatted_group.split("__")[-1]
                data_entry[original_group] = phone.get(formatted_group)
            data_entry["count"] = phone["count"]
            data.append(data_entry)

    # Apply pagination to the data
    else:
        data = [
            {
                "pk": device.pk,
                "imei": device.imei,
                "model": device.sku.model,
                "capacity": device.sku.capacity,
                "color": device.sku.color,
                "grade": device.sku.grade,
                "battery": device.battery,
                "status": (
                    device.deviceStatus.status if device.deviceStatus else "Unknown"
                ),
                "so": device.so.so if device.so else None,
                "so_id": device.so.pk if device.so else None,
                "count": 1,
            }
            for device in phones[start : start + length]
        ]

    # Get the total count of records (for pagination info)
    total_records = phones.count()

    response_data = {
        "data": data,
        "grouping": grouping,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,  # Set this to the filtered count if applicable
    }

    return JsonResponse(response_data)


def updateStatus(request):
    if request.method == "POST":
        selected_pks = request.POST.getlist("pks")
        status = request.POST.get("status")
        print(selected_pks)
        try:
            # Update the status of devices with the selected PKs
            devicesToUpdate = devices.all_objects.filter(pk__in=selected_pks)
            devicesToUpdate.update(deviceStatus=status)
            message = "Devices updated successfully."
            return JsonResponse({"message": message})
        except Exception as e:
            message = "Error updating devices."
            return JsonResponse({"message": message, "error": str(e)}, status=500)


def updateGrade(request):
    if request.method == "POST":
        selected_pks = request.POST.getlist("pks")
        grade = request.POST.get("grade")
        try:
            # Update the status of devices with the selected PKs
            devicesToUpdate = devices.objects.filter(pk__in=selected_pks)
            newSKUs = []
            for device in devicesToUpdate:

                new_device_attributes, created = deviceAttributes.objects.get_or_create(
                    model=device.sku.model,
                    color=device.sku.color,
                    capacity=device.sku.capacity,
                    grade=grade,
                )
                device.sku = new_device_attributes
                device.save()
                if created:
                    newSKUs.append(new_device_attributes)
            message = "Devices updated successfully."
            return JsonResponse({"message": message})
        except Exception as e:
            message = "Error updating devices."
            return JsonResponse({"message": message, "error": str(e)}, status=500)


def deleteDevices(request):
    if request.method == "POST":
        selected_pks = request.POST.getlist("pks")
        print(selected_pks)

        try:
            # Update the status of devices with the selected PKs
            devicesToDelete = devices.objects.filter(pk__in=selected_pks)
            status = deviceStatus.objects.get(status="Deleted")
            devicesToDelete.update(deviceStatus=status)
            message = "Devices deleted successfully."
            return JsonResponse({"message": message})
        except Exception as e:
            message = "Error updating devices."
            return JsonResponse({"message": message, "error": str(e)}, status=500)


def sales(request):
    return render(request, template_name="sales.html")


def salesajax(request):
    # Extract parameters sent by DataTables
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))  # Default page size

    search_value = request.GET.get("search[value]", None)

    # Your data filtering and processing logic here

    status = request.GET.getlist("status[]", None)
    order = request.GET.get("order[0][column]", None)
    sales = (
        salesOrders.objects.all().select_related("customer").prefetch_related("items")
    )

    # Apply additional filtering based on the search query
    if search_value:
        sales = sales.filter(so__icontains=search_value)
    total_records = sales.count()

    data = [
        {
            "pk": so.pk,
            "order_id": so.so,
            "order_date": so.date_created,
            "channel": so.customer.channel,
            "customer": so.customer.name,
            "quantity": sum([item.quantity for item in so.items.all()]),
            "state": so.state,
        }
        for so in sales[start : start + length]
    ]

    response_data = {
        "data": data,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,  # Set this to the filtered count if applicable
    }

    return JsonResponse(response_data)


def listings(request):

    last_updated = BackMarketListing.history.latest().history_date
    context = {"last_updated": last_updated}

    return render(request, context=context, template_name="listings.html")


def BMlistingsajax(request):
    page_length = int(request.GET.get("length", 10))
    start = int(request.GET.get("start", 0))

    # Get All Suitable Stock from Elite Inventory
    groupedStock = (
        devices.objects.filter(deviceStatus=2, battery__gte=85)
        .exclude(sku__grade__in=["ABC", "C"])
        .values("sku__sku")
        .annotate(count=Count("sku"))
    )
    # Convert to dictionary for easy lookup
    groupedStockDict = {item["sku__sku"]: item["count"] for item in groupedStock}

    data = []
    # Get Backmarket Listings with stock (note, this may be old data)

    listings = BackMarketListing.objects.filter(quantity__gt=0).order_by("quantity")

    # Iterate through listings and check if there is stock in Elite Inventory
    for listing in listings:
        try:
            # Check if there is a linked SKU
            sku = listing.sku.sku
        except:
            sku = None
        listing = {
            "SKU": sku,
            "listing_id": listing.listing_id,
            "product_name": listing.title.replace(" - Unlocked", ""),
            "stock_listed": listing.quantity,
            "stock_available": 0,
        }
        # If there's a matching SKU get the available stock and remove it from the dictionary
        if sku:
            listing["stock_available"] = groupedStockDict.get(sku, 0)
            if sku in groupedStockDict:
                groupedStockDict.pop(sku)
        else:
            listing["stock_available"] = "SKU Mismatch"
        data.append(listing)

    # Find the BM Listing Data of the SKUs that are not online
    nonelisted = BackMarketListing.objects.filter(
        sku__sku__in=groupedStockDict.keys()
    ).values("sku__sku", "title", "listing_id")

    # Create a dictionary of the nonelisted SKUs for easy lookup
    nonelistedDict = {
        item["sku__sku"]: (item["title"], item["listing_id"]) for item in nonelisted
    }
    # Iterate through the nonelisted SKUs and add them to the data
    for sku, count in groupedStockDict.items():
        listing = {
            "SKU": sku,
            "listing_id": nonelistedDict.get(sku, (0, "Missing SKU on BM"))[1],
            "product_name": nonelistedDict.get(sku, ("Missing SKU on BM", 0))[
                0
            ].replace(" - Unlocked", ""),
            "stock_listed": 0,
            "stock_available": count,
        }
        data.append(listing)
    sortedData = sorted(data, key=lambda d: d["stock_listed"], reverse=True)
    print(sortedData)
    total_records = len(data)
    response_data = {
        "data": sortedData[start : page_length + start],
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
    }

    return JsonResponse(response_data)


def updateBMquantity(request):
    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        quantity = request.POST.get("quantity")
        try:
            response = BM.update_listing(listing_id, quantity)
            print(response)
            message = "Quantity updated successfully."
            return JsonResponse({"message": message})
        except Exception as e:
            message = "Error updating quantity."
            return JsonResponse({"message": message, "error": str(e)}, status=500)


def getBMdata(request):
    BM.get_listings()
    return JsonResponse({"message": "Data updated successfully."})


def addStockImeis(request):
    if not request.GET.get("retry"):

        imeis = request.POST.getlist("imeis")
        # Replace \r\n with \n, then join and split by newlines
        imeis_string = "\n".join(imeis).replace("\r\n", "\n")
        imeis_lines = imeis_string.splitlines()

        # Flatten the list, split by commas, and remove any empty entries or extra spaces
        imeiscleaned = [
            item.strip()  # Remove any leading/trailing whitespace
            for sublist in [line.split(",") for line in imeis_lines]
            for item in sublist
            if item.strip() != ""  # Ensure the item is not empty after stripping
        ]

        # Join the cleaned IMEIs into a single string separated by commas
        imeis_string = ",".join(imeiscleaned)
        devices = PC.getBulkIMEI(imeis_string)

    else:
        devices = {}
        missingSkus = request.session.get("missing_sku")
        for entry in missingSkus:
            devices.update(entry["devices"][0])

    uploaded, grouped_missing_skus, missing_po, duplicate_devices = PC.addToDB(devices)
    request.session["missing_sku"] = grouped_missing_skus

    context = {
        "upload": uploaded,
        "missing": grouped_missing_skus,
        "po": missing_po,
        "duplicate": duplicate_devices,
    }

    return render(request, context=context, template_name="upload.html")


def getBmOrders(request):
    shipment.objects.all().delete()
    salesOrders.objects.all().delete()
    customer.objects.all().delete()
    BM.get_orders()
    return render(request, template_name="sales.html")


def get_label(request, so):
    shipment_instance = shipment.objects.get(so_id=so)
    file_buffer = shipment_instance.get_label()

    # Serve the PDF directly without streaming
    response = FileResponse(
        file_buffer,
        content_type="application/pdf",
        filename=f"{shipment_instance.label_blob_name}",
    )
    response["Content-Disposition"] = (
        f'inline; filename="{shipment_instance.label_blob_name}"'
    )
    return response


class orderDetail(DetailView):
    template_name = "order_detail.html"
    queryset = (
        salesOrders.objects.select_related(
            "customer__shipping_address",
            "customer__currency",
        )
        .prefetch_related("items", "devices")
        .all()
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_quantity = sum(item.quantity for item in context["object"].items.all())
        context["total_quantity"] = total_quantity
        return context


def shipmentDetails(request, shipment_id):

    shipment_in = shipment.objects.get(so_id=int(shipment_id))
    context = model_to_dict(shipment_in)
    html_snippet = render_to_string("./snippets/shipment_details.html", context)

    return HttpResponse(html_snippet)


def updateAddress(request):
    # Ensure the request method is POST to handle form submission
    if request.method == "POST":
        payload = request.POST.dict()
        customer_id = payload.pop("customer_id", None)

        # Get Customer
        customer_instance = customer.objects.get(pk=customer_id)

        address_id = customer_instance.shipping_address.pk

        # Construct a dictionary of fields to update
        updated_fields = {key: value for key, value in payload.items()}

        # Use the update() method on a queryset that targets only the specific address instance
        address.objects.filter(pk=address_id).update(**updated_fields)

        # Retrieve the updated address object
        updated_address = address.objects.get(pk=address_id)

        # Convert the updated address object to a dictionary
        # You might want to explicitly specify which fields to include if there are any you want to exclude
        address_data = model_to_dict(updated_address)

        return JsonResponse(address_data)


def getShippingRates(request):

    customer = request.POST.get("customer")
    response = DHL.get_available_shipping(customer)
    if response.status_code == 400:
        error = json.loads(response.content.decode("utf-8"))["detail"]
        print(error)
        return JsonResponse({"error": error}, status=response.status_code, safe=False)

    else:
        sorted_services = json.loads(response.content.decode("utf-8"))
        print(sorted_services)
        html_snippet = render_to_string(
            "./snippets/shipping_options.html", sorted_services
        )

        return HttpResponse(html_snippet)


def buyShippingLabel(request):
    customerId = request.GET.get("customer")
    shipping_service = request.GET.get("shipping_service")
    so = request.GET.get("salesOrder")

    DHL.buy_shipping_label(customerId, shipping_service, so)

    BM.update_orders(so)
    
    return JsonResponse({"so": so})


def commitImei(request):
    if request.method == "POST":
        imei = request.POST.get("imei")
        so_id = request.POST.get("so_id")
        item_id = request.POST.get("item_id")
        soldSku = request.POST.get("sku")
        force_commit = request.POST.get("force_commit", "false")
        try:
            device = devices.all_objects.get(imei=imei)
            if not device.deviceStatus.sellable:
                message = f"IMEI is not sellable.\n Listed as: <strong>{device.deviceStatus.status}</strong>"
                return JsonResponse({"message": message}, status=400)
            if device.sku.sku != soldSku and force_commit == "false":
                message = (
                    f"Mismatch! \n Scanned IMEI: {device.sku.sku}, Sold As: {soldSku}"
                )
                return JsonResponse({"message": message}, status=400)
            device.so_id = so_id
            device.deviceStatus_id = 5
            device.sales_order_item_id = item_id
            device.save()
            message = "IMEI committed successfully."
            return JsonResponse({"message": message})
        except Exception as e:
            message = "Error committing IMEI:\n"
            return JsonResponse(
                {"message": message + " " + str(e), "error": str(e)}, status=500
            )


def removeImei(request):
    device_id = request.POST.get("device")
    deviceIn = devices.all_objects.get(pk=device_id)
    deviceIn.so_id = None
    deviceIn.sales_order_item_id = None
    deviceIn.deviceStatus_id = 1
    deviceIn.save()
    return JsonResponse({"message": "IMEI removed successfully."})
