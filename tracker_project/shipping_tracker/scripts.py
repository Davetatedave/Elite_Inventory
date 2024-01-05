
from .keys import phonecheck_api_key
import requests
import json
import datetime
import pandas as pd
import math
from .models import deviceAttributes

# This script is used to import devices from the PhoneCheck API


def getPCResults(date_start=None, date_finish=None, po_number=None):
    td = datetime.datetime.today()
    today = td.strftime("%Y-%m-%d")
    if date_start:
        date = {"date_start": date_start, "date_finish": today}
        if date_finish:
            date["date_finish"] = date_finish
    else:
        date = {"Date": today}
    reqUrl = "https://clientapiv2.phonecheck.com/cloud/CloudDB/v2/GetAllDevices/"

    headersList = {"Content-Type": "application/json"}

    payload = json.dumps(
        {"Apikey": "76d9b060-3417-475c-881c-7403463a0f2e", "Username": "elite2","limit":10, **date}
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
        model__iexact=model,
        color=colour,
        capacity=capacity,
        grade=grade
    )
    
    # Check if a matching record was found
    if matching_records.exists():
        SKU = matching_records.first()  # Get the first matching record
        return SKU.sku
    else:
        raise ValueError("No matching record found")