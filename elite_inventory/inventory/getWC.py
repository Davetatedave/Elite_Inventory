import requests
from inventory import models

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
    models.devices(
        imei=phone["esn"],
        sku=phone["sku"],
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

models.devices.objects.bulk_create(phones)
