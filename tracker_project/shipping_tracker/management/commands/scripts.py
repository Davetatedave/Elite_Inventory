
from keys import phonecheck_api_key
import requests
import json
import datetime
import pandas as pd
import math

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

df = getPCResults()[0]

# Initialize a dictionary to store inferred data types
data_types = {}

# Infer data types for each field
for key, value in df.items():
    try:
        # Attempt to infer integer type
        int_value = int(value)
        data_types[key] = (value,int)
    except:
        try:
            # Attempt to infer float type
            float_value = float(value)
            data_types[key] = (value,float)
        except:
            try:
                # Attempt to infer datetime type
                datetime_value = pd.to_datetime(value, errors='raise')
                data_types[key] = (value,'datetime64')
            except (ValueError, TypeError):
                # If all attempts fail, default to string
                data_types[key] = (value,str)

print(data_types)


# # Infer data types
# typed = single.infer_objects()

# # Get the data types of each column
# types = typed.dtypes

# # Print the data types
# print(set(types))