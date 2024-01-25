from django.shortcuts import render
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
)
from datetime import datetime, timedelta
from django.views.generic import ListView, DetailView, UpdateView
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .scripts import PhoneCheckAPI as PC, calculateSKU, BackMarketAPI as BM
from .forms import FilterForm
from collections import defaultdict
from django.dispatch import receiver
from django.db.models.signals import post_save


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
        sku = request.POST.get("sku")
        devicesUpload = request.POST.getlist("devices")
        try:
            new_sku = deviceAttributes(
                model=model, capacity=capacity, color=color, grade=grade, sku=sku
            )
            new_sku.save()
            message = "SKU added successfully."
            if devicesUpload:
                for device in devicesUpload:
                    upload_device = devices(
                        imei=device["IMEI"],
                        sku_id=new_sku,
                        deviceStatus_id=3 if device["Working"] == "Yes" else 2,
                        battery=device["BatteryHealthPercentage"],
                        date_tested=datetime.strptime(
                            device["CreatedTimeStamp"].split("T")[0], "%Y-%m-%d"
                        ),
                        working=True
                        if device["Working"] == "Yes"
                        else False
                        if device["Working"] == "No"
                        else None,
                        po=po_instance,
                        warehouse_id=warehouse,
                    )

            return JsonResponse({"message": message})
        except Exception as e:
            message = "Error adding SKU."
            return JsonResponse({"message": message, "error": str(e)}, status=500)


def addStock(request):
    return render(request, template_name="add_stock.html")


def inventoryOLD(request):
    filter_form = FilterForm()

    models = request.GET.get("models", None)

    device_attributes = deviceAttributes.objects.all()

    device_stauses = deviceStatus.objects.all()
    device_statuses = serializers.serialize("json", device_stauses)
    breakpoint()
    print(device_statuses)

    if models:
        device_attributes = device_attributes.filter(model=models)

    distinct_values = {
        field.name: set(getattr(obj, field.name) for obj in device_attributes)
        for field in deviceAttributes._meta.fields
    }
    distinct_values["status"] = set(device_statuses)

    context = {
        "device_list": devices.objects.select_related("sku").all(),
        "device_attributes": distinct_values,
        "filter_form": filter_form,
    }
    return render(request, context=context, template_name="inventory.html")


def inventory(request):
    models = request.GET.get("models", None)

    device_attributes = deviceAttributes.objects.all()
    statuses = deviceStatus.objects.all()

    statusesfortable = serializers.serialize("json", deviceStatus.objects.all())

    if models:
        device_attributes = device_attributes.filter(model=models)

    distinct_values = {
        field.name: set(getattr(obj, field.name) for obj in device_attributes)
        for field in deviceAttributes._meta.fields
    }

    distinct_values["status"] = statuses = [status.status for status in statuses]

    context = {
        "device_attributes": distinct_values,
        "statuses": statusesfortable,
    }
    return render(request, context=context, template_name="inventory.html")


def inventoryAjax(request):
    # Extract parameters sent by DataTables
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))  # Default page size

    search_value = request.GET.get("search[value]", None)
    bulk_search_value = request.GET.getlist("bulk_search_value", None)

    # Your data filtering and processing logic here

    models = request.GET.getlist("model[]", None)
    grades = request.GET.getlist("grade[]", None)
    colors = request.GET.getlist("color[]", None)
    batteryA = request.GET.get("batteryA", None)
    batteryB = request.GET.get("batteryB", None)
    status = request.GET.getlist("status[]", None)
    order = request.GET.get("order[0][column]", None)
    grouping = request.GET.getlist("grouping[]", None)

    if "Deleted" in status:
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
                "status": device.deviceStatus.status
                if device.deviceStatus
                else "Unknown",
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
            devicesToUpdate = devices.objects.filter(pk__in=selected_pks)
            devicesToUpdate.update(deviceStatus=status)
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


def listings(request):
    @receiver(post_save, sender=BackMarketListing)
    def test(sender, instance, **kwargs):
        print(sender, instance)

    return render(request, template_name="listings.html")


def BMlistingsajax(request):
    page_length = int(request.GET.get("length", 10))
    start = int(request.GET.get("start", 0))
    listings, total = BM.get_listings(start, page_length)

    groupedStock = (
        devices.objects.filter(deviceStatus=3)
        .values("sku")
        .annotate(count=Count("sku"))
    )
    groupedStockDict = {item["sku"]: item["count"] for item in groupedStock}
    print(groupedStockDict)

    data = []

    for listing in listings:
        try:
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
        if sku:
            listing["stock_available"] = groupedStockDict.get(sku, 0)
            if sku in groupedStockDict:
                groupedStockDict.pop(sku)
        else:
            listing["stock_available"] = "SKU Mismatch"
        data.append(listing)
    nonelisted = BackMarketListing.objects.filter(
        sku__in=groupedStockDict.keys()
    ).values("sku", "title", "listing_id")
    nonelistedDict = {
        item["sku"]: (item["title"], item["listing_id"]) for item in nonelisted
    }

    for sku, count in groupedStockDict.items():
        listing = {
            "SKU": sku,
            "listing_id": nonelistedDict.get(sku, "Missing SKU on BM")[1],
            "product_name": nonelistedDict.get(sku, "Missing SKU on BM")[0].replace(
                " - Unlocked", ""
            ),
            "stock_listed": 0,
            "stock_available": count,
        }
        data.append(listing)

    total_records = len(data)
    response_data = {
        "data": data[start : page_length + start],
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


def addStockImeis(request):
    if request.method == "POST":
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

        df = PC.getBulkIMEI(imeis_string)

        uploaded, grouped_missing_skus, missing_po, duplicate_devices = PC.addToDB(df)

        context = {
            "upload": uploaded,
            "missing": grouped_missing_skus,
            "po": missing_po,
            "duplicate": duplicate_devices,
        }

    return HttpResponse(context)
