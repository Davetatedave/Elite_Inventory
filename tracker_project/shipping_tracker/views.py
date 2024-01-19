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
)
from datetime import datetime, timedelta
from django.views.generic import ListView, DetailView, UpdateView
from django.db.models import Count
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .scripts import getPCResults, calculateSKU
from .forms import FilterForm
from collections import defaultdict


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
    warehouse = request.GET.get("warehouse", None)
    df = getPCResults(start, end, po)

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
    return render(request, template_name="listings.html")


def BMlistingsajax(request):
    return JsonResponse(
        {
            "draw": 1,
            "recordsTotal": 100,
            "recordsFiltered": 50,
            "data": [
                {
                    "pk": 1,
                    "SKU": "IP12128BAB",
                    "product_name": "iPhone 12 128GB Black A/B Grade",
                    "price": "100.00",
                    "stock_listed": "20",
                    "stock_available": "22",
                },
                {
                    "pk": 2,
                    "SKU": "IP12128BBC",
                    "product_name": "iPhone 12 128GB Black B/C Grade",
                    "price": "150.00",
                    "stock_listed": "15",
                    "stock_available": "18",
                },
            ],
        }
    )
