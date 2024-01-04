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
from .scripts import getPCResults, calculateSKU


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


class ShippingDetailView(DetailView):
    model = trackingDb
    template_name = "trackingdb_detail.html"


def phoneCheck(request):
    start = request.GET.get("pCStart", None)
    end = request.GET.get("pCEnd", None)
    po = request.GET.get("po", None)

    df = getPCResults(start, end, po)
    print(df[1])
    
    phone=[{
        "Erased": "Yes",
        "Type": "iOS Secure Erase",
        "StartTime": "2024-01-04 16:24:34",
        "EndTime": "2024-01-04 16:25:48",
        "RestoreCode": "",
        "erasedNotes": "",
        "erasedSD": "",
        "VendorName": "SH",
        "InvoiceNo": "PO-00591",
        "StationID": "elite3",
        "isCloudTransaction": "0",
        "BoxNo": "",
        "QTY": "",
        "Working": "Yes",
        "Passed": "Accelerometer,Bluetooth,Bottom Mic Quality,C-Back Glass Damaged?,C-Camera Glass Damaged?,C-Is the Device Bent or Damaged?,Custom Tests,Digitizer,Ear Speaker,Earpiece Quality,Face ID,Flashlight,Flip Switch,Front Camera,Front Camera Quality,Front Mic Quality,Front Microphone,Front Video Camera,Glass Cracked,Grading,Gyroscope,LCD,Loud Speaker,Microphone,NFC,Network Connectivity,Power Button,Proximity Sensor,Rear Camera,Rear Camera Quality,Rear Mic Quality,Rear Video Camera,Recording Quality,Screen Rotation,Sim Reader,Telephoto Camera,Telephoto Camera Quality,Ultra Wide Camera Quality,UltraWide Camera,Vibration,Video Microphone,Volume Down Button,Volume Up Button,Wifi",
        "Failed": "",
        "Pending": "",
        "TransactionID": "549",
        "master_id": "1342",
        "WareHouse": "",
        "MasterName": "Elite Innovations",
        "Model": "iPhone 13 Pro",
        "Memory": "128GB",
        "IMEI": "353990998908920",
        "Carrier": "",
        "Serial": "C2P0R6RGF7",
        "UDID": "00008110-0006388E229B801E",
        "LicenseIdentifier": "6388E229B801E",
        "DeviceLock": "Off",
        "AppleID": "",
        "Rooted": "Off",
        "Color": "Graphite",
        "Grade": "A",
        "Version": "17.1.1",
        "OS": "iOS",
        "Make": "Apple",
        "Firmware": "3.10.02",
        "Notes": "",
        "ESN": "No License",
        "DeviceCreatedDate": "2024-01-04 16:11:54",
        "DeviceUpdatedDate": "2024-01-04 16:25:10",
        "BatteryPercentage": "4",
        "BatteryCycle": "392",
        "BatteryHealthPercentage": "85",
        "BatteryDesignMaxCapacity": "3076",
        "BatteryCurrentMaxCapacity": "2626",
        "BatterySerial": "F8Y150709R013RFB7",
        "BatteryModel": "N/A",
        "BatterySource": "PD01",
        "UnlockStatus": "",
        "TesterName": "Emma",
        "Cosmetics": "",
        "BuildNo": "2.2.15.15",
        "AppVersion": "3.0.669",
        "ManualEntry": "No",
        "ESNResponse": [
            {
                "isLicenseExpired": True,
                "message": "User has exceeded esn limit",
                "FieldColor": "Orange",
            }
        ],
        "SimLockResponse": "",
        "LPN": "",
        "Custom1": "A2483",
        "SKUCode": "IP13P128GRAA",
        "RegulatoryModelNumber": "A2483",
        "CosmeticsFailed": "",
        "CosmeticsPassed": "",
        "CosmeticsPending": "",
        "CosmeticsWorking": "",
        "Network": "T-Mobile",
        "Network1": "Locked",
        "Network2": "Locked",
        "SIM1MCC": "",
        "SIM1MNC": "",
        "SIM2MCC": "",
        "SIM2MNC": "",
        "SIM1Name": "",
        "SIM2Name": "",
        "IMEI2": "353990998146471",
        "SimTechnology": "GSM/CDMA",
        "BatteryTemperature": "30",
        "AvgBatteryTemperature": None,
        "MaxBatteryTemperature": None,
        "MinBatteryTemperature": None,
        "BatteryResistance": "14",
        "MEID": "35399099890892",
        "MEID2": "35399099814647",
        "PESN": "80141609",
        "PESN2": "80C27229",
        "SIMSERIAL": "8944303483092867865",
        "SIMSERIAL2": "",
        "DecimalMEID": "089296501708980626",
        "DecimalMEID2": "089296501708472135",
        "SimErased": "Yes",
        "MDM": "No",
        "CountryOfOrigin": "US",
        "BatteryDrainDuration": "",
        "BatteryChargeStart": "",
        "BatterChargeEnd": "",
        "BatteryDrain": "",
        "WifiMacAddress": "48:35:2b:69:a2:b5",
        "SimHistory": None,
        "iCloudInfo": "\n",
        "BatteryDrainInfo": "",
        "CompatibleSim": "",
        "NotCompatibleSim": "",
        "DeviceState": "No",
        "BatteryDrainType": "",
        "CocoCurrentCapacity": "2626",
        "CocoDesignCapacity": "0",
        "OEMBatteryHealth": "0.0",
        "CocoBatteryHealth": "0.0",
        "PortNumber": "3",
        "startHeat": "",
        "endHeat": "",
        "ProductCode": "",
        "device_shutdown": "",
        "SimLock": "",
        "BMic": "0.6403",
        "VMic": "0.583",
        "FMic": "0.5854",
        "DefectsCode": "",
        "ManualFailure": "No",
        "ErrorCode": "New Bank Retail",
        "ScreenTime": "",
        "testerDeviceTime": "",
        "gradePerformed": "0",
        "isLabelPrint": "0",
        "Knox": "",
        "TestPlanName": "",
        "CarrierLockResponse": "null",
        "Parts": '{"Remarks":"Genuine","Data":[{"currentCheckSum":"null","Status":"Genuine","name":"Serial Number","FactorySerial":"C2P0R6RGF7*","checkSum":"null","notice":"","CurrentSerial":"C2P0R6RGF7"},{"currentCheckSum":"","Status":"Genuine","name":"Main Board","FactorySerial":"F3Y20671AHT0G49A*","checkSum":"null","notice":"","CurrentSerial":"F3Y20671AHT0G49A"},{"currentCheckSum":"MTNSRg==","Status":"Genuine","name":"Battery","FactorySerial":"F8Y150709R013RFB7*","checkSum":"null","notice":"","CurrentSerial":"F8Y150709R013RFB7"},{"currentCheckSum":"UTdINQ==","Status":"Genuine","name":"Front Camera","FactorySerial":"DNM20227475Q7H56N*","checkSum":"null","notice":"","CurrentSerial":"DNM20227475Q7H56N"},{"currentCheckSum":"UTFOTQ==","Status":"Genuine","name":"Back Camera","FactorySerial":"DN82057H225Q1NMDW*","checkSum":"null","notice":"","CurrentSerial":"DN82057H225Q1NMDW"},{"currentCheckSum":"MTdWUA==","Status":"Genuine","name":"LCD","FactorySerial":"FXV15010CNW17VP97+0A065280000129001052597263*","checkSum":"null","notice":"","CurrentSerial":"FXV15010CNW17VP97+0A065280000129001052597263"}]}',
        "Ram": None,
        "IFT_Codes": None,
        "GradingResults": None,
        "grade_profile_id": None,
        "grade_route_id": None,
        "transaction_type": None,
        "final_price": "0.0",
        "old_deviceDisconnect": None,
        "deviceDisconnect": "2024-01-04 16:25:09",
        "CreatedAPITimeStamp": None,
        "UpdatedAPITimeStamp": None,
        "EID": "89049032007008882600096881765556",
        "eBayRefurbished": "Excellent",
        "eBayRejection": "N/A",
        "amazonRenewed": "Amazon Renewed",
        "amazonRenewedRejection": "N/A",
        "checkall": "00000000000",
        "MDMResponse": '{"MDMCloudConfig":"MDMCloudConfig:","dict":"CloudConfiguration  AllowPairing : true CloudConfigurationUIComplete : true ConfigurationWasApplied : true IsMDMUnremovable : false IsMandatory : true IsSupervised : false PostSetupProfileWasInstalled : true ","dict1":"OrganizationNamer : PhoneCheck Statusr : Acknowledged ","dict2":""}',
        "BatteryHealthGrade": None,
        "androidCarrierId": None,
        "swappaQualified": "swappaQualified",
        "swappaRejection": "N/A",
        "backMarketQualified": "BackMarket Qualified",
        "backMarketRejection": "N/A",
        "start_battery_charge": None,
        "end_battery_charge": None,
        "total_battery_drain": None,
        "warranty": "",
        "data_verification": None,
        "ModelNo": "MLR23LL/A",
        "PackageName": "New Bank Retail",
        "InitialCarrier": "N/A",
        "CosmeticsSettings": [],
        "A4Reports": "91385885",
        "CreatedTimeStamp": "2024-01-04T16:25:09.00+00:00",
        "UpdatedTimeStamp": "2024-01-04T16:25:10.00+00:00",
        "A4ReportLink": "https://cloudportal.phonecheck.com/cloud/reporting/A4-certificate/RjFockVxRU9lZ2Myam0rbVN1emRDUT09",
        "erasureReportLink": "https://cloudportal.phonecheck.com/cloud/reporting/erasure-report/RjFockVxRU9lZ2Myam0rbVN1emRDUT09",
        "dhr_link": "https://historyreport.phonecheck.com/report-qr/debd475e-ab1b-11ee-926d-06d6a17a84bb",
    }]

    for device in phone:
        breakpoint()
        try:
            {
                "imei": device["IMEI"],
                "sku": calculateSKU(device),
                "status": device["status"],
            }
        except:
            pass

    return HttpResponse(df)
