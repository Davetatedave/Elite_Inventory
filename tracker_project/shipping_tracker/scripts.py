from .keys import phonecheck_api_key
import requests
import json
import datetime
import pandas as pd
import math
from .models import deviceAttributes, devices, purchaseOrders, faults
from collections import defaultdict

# This script is used to import devices from the PhoneCheck API


def getPCResults(date_start=None, date_finish=None, po_number=None):
    td = datetime.datetime.today()
    today = td.strftime("%Y-%m-%d")
    if date_start:
        date = {"startdate": str(date_start), "enddate": today}
        if date_finish:
            date["enddate"] = str(date_finish)
    else:
        date = {"Date": today}
    reqUrl = "https://clientapiv2.phonecheck.com/cloud/CloudDB/v2/GetAllDevices/"

    headersList = {"Content-Type": "application/json"}

    payload = json.dumps(
        {
            "Apikey": "76d9b060-3417-475c-881c-7403463a0f2e",
            "Username": "elite2",
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
    print(phones[0])
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
