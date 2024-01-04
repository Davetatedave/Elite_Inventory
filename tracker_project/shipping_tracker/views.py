from django.shortcuts import render
from django.core import serializers
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from .models import trackingDb
from datetime import datetime, timedelta
from django.views.generic import ListView, DetailView, UpdateView
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string
from scripts import getPCResults, calculateSKU

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
    group_status = request.GET.get("grouped","individual")

    if group_status != 'individual':
        print('grouped')
        queryset = queryset.values(group_status).annotate(count=Count(group_status)).order_by("-count")

    page = request.GET.get("page", 1)
    paginator = Paginator(queryset, 10)
    table_info = paginator.get_page(page)
    statuses=trackingDb.objects.values_list('Arrival_Status', flat=True).distinct()

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
    
    data=trackingDb.objects.all()
    columns = [f for f in trackingDb._meta.fields]
    page=request.GET.get("page",1)
    paginator=Paginator(data,10)
    table_info = paginator.get_page(page)
    context={
        "page_title": "Welcome",
        "table_data": table_info,
        "paginator": paginator,
        "columns": columns,
    }

    return render(request,context=context,template_name="shipping.html")

class ShippingDetailView(DetailView):
    model = trackingDb
    template_name = "trackingdb_detail.html"

def phoneCheck(request):
    
    start=request.GET.get("pCStart",None)
    end=request.GET.get("pCEnd",None)
    po=request.GET.get("po",None)
    
    df = getPCResults(start,end,po)
    
    for device in df:
        try:
            {"imei":device["imei"],
            "sku":calculateSKU(device),
            "status":device["status"]}
        except:
            pass
        
    return HttpResponse(df)