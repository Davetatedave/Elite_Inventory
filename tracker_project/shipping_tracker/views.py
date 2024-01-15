from django.shortcuts import render
from django.core import serializers
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from .models import trackingDb, devices, deviceAttributes, deviceStatus
from datetime import datetime, timedelta
from django.views.generic import ListView, DetailView, UpdateView
from django.db.models import Count
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .scripts import getPCResults, calculateSKU
from .forms import FilterForm


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

    df = getPCResults(start, end, po)
    missing_sku = []
    to_upload = []
    duplicate_devices = []

    print(df[0])
    for device in df:
        try:
            sku_instance = deviceAttributes.objects.get(sku=calculateSKU(device))
            new_device = devices(
                imei=device["IMEI"],
                sku=sku_instance,
                deviceStatus_id=2,
                battery=device["BatteryHealthPercentage"],
            )
            new_device.save()
            to_upload.append(device["IMEI"])

        except ValueError as e:
            print(e)
            missing_sku.append((device["SKUCode"], device["IMEI"]))

        except IntegrityError as e:
            duplicate_devices.append(device["IMEI"])

        except Exception as e:
            print(e)

    context = {
        "upload": to_upload,
        "missing": missing_sku,
        "duplicate": duplicate_devices,
    }

    return render(request, context=context, template_name="upload.html")


def inventory(request):
    filter_form = FilterForm()

    models = request.GET.get("models", None)

    device_attributes = deviceAttributes.objects.all()

    if models:
        device_attributes = device_attributes.filter(model=models)

    distinct_values = {
        field.name: set(getattr(obj, field.name) for obj in device_attributes)
        for field in deviceAttributes._meta.fields
    }

    context = {
        "device_list": devices.objects.select_related("sku").all(),
        "device_attributes": distinct_values,
        "filter_form": filter_form,
    }
    return render(request, context=context, template_name="inventory.html")


def inventory2(request):
    models = request.GET.get("models", None)

    device_attributes = deviceAttributes.objects.all()
    statuses = serializers.serialize("json", deviceStatus.objects.all())

    if models:
        device_attributes = device_attributes.filter(model=models)

    distinct_values = {
        field.name: set(getattr(obj, field.name) for obj in device_attributes)
        for field in deviceAttributes._meta.fields
    }

    context = {
        "device_attributes": distinct_values,
        "statuses": statuses,
    }
    return render(request, context=context, template_name="inventory2.html")


def inventoryAjax(request):
    # Extract parameters sent by DataTables
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))  # Default page size

    search_value = request.GET.get("search[value]", None)

    # Your data filtering and processing logic here

    models = request.GET.getlist("model[]", None)
    grades = request.GET.getlist("grade[]", None)
    colors = request.GET.getlist("color[]", None)
    batteryA = request.GET.get("batteryA", None)
    batteryB = request.GET.get("batteryB", None)
    order = request.GET.get("order[0][column]", None)

    phones = devices.objects.select_related("sku").select_related("deviceStatus").all()

    # Apply additional filtering based on the search query
    if search_value:
        # Example: Filter based on the 'imei' field
        phones = phones.filter(imei__icontains=search_value)

    if models:
        phones = phones.filter(sku__model__in=models)

    if grades:
        phones = phones.filter(sku__grade__in=grades)

    if colors:
        phones = phones.filter(sku__color__in=colors)
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

    # Apply pagination to the data
    data = [
        {
            "pk": device.pk,
            "imei": device.imei,
            "model": device.sku.model,
            "capacity": device.sku.capacity,
            "color": device.sku.color,
            "grade": device.sku.grade,
            "battery": device.battery,
            "status": device.deviceStatus.status if device.deviceStatus else "Unknown",
        }
        for device in phones[start : start + length]
    ]

    # Get the total count of records (for pagination info)
    total_records = phones.count()

    response_data = {
        "data": data,
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
            devicesToDelete.update(status="Deleted")
            message = "Devices deleted successfully."
            return JsonResponse({"message": message})
        except Exception as e:
            message = "Error updating devices."
            return JsonResponse({"message": message, "error": str(e)}, status=500)
