import requests
from models import devices
from django.core.management.base import BaseCommand
from inventory.models import deviceAttributes
from .scripts import calculateSKU


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

    phones = [
        devices(
            imei=phone["esn"],
            sku=calculateSKU(
                {
                    "Model": phones["sku"],
                    "Color": phones["color"],
                    "Memory": phones["memory"],
                    "Grade": phones["grade"],
                }
            ),
            deviceStatus=phone["status"],
            battery=phone["battery"],
            date_added=phone["date_added"],
            date_tested=phone["date_tested"],
            working=phone["working"],
            po=phone["po"],
            so=phone["so"],
            warehouse=phone["warehouse"],
        )
        for phone in phones
    ]

    print(imeis)

    return phones
