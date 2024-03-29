import datetime
import requests
import traceback


def get_mock():
    mock_response = {
        "shipmentTrackingNumber": "6850596701",
        "trackingUrl": "https://express.api.dhl.com/mydhlapi/shipments/6850596701/tracking",
        "packages": [
            {
                "referenceNumber": 1,
                "trackingNumber": "JD014600011437536769",
                "trackingUrl": "https://express.api.dhl.com/mydhlapi/shipments/6850596701/tracking?pieceTrackingNumber=JD014600011437536769",
            }
        ],
        "documents": [
            {
                "imageFormat": "PDF",
                "content": "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",
                "typeCode": "label",
            }
        ],
    }
    return mock_response


deliveredStatuses = {
    "Customer was not available when ups attempted delivery. will deliver to a nearby ups access point™ for customer coll.",
    "Delivered",
    "Delivered ",
    "Delivered to ups access point™ ",
    "Delivery attempt could not be completed",
    "Delivery attempted but no response at consignee address",
    "Delivery attempted – consignee premises closed",
    "Delivery not accepted",
    "Out for delivery",
    "Out for delivery today",
    "Shipment is out with courier for delivery",
}

datesRe = requests.get("https://www.gov.uk/bank-holidays.json").json()[
    "england-and-wales"
]


holiday_dates = [
    datetime.datetime.strptime(i["date"], "%Y-%m-%d") for i in datesRe["events"]
]


def parse_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d")


def find_first_delivery_attempt(data):
    deliveredStatuses = {
        "Customer was not available when ups attempted delivery. will deliver to a nearby ups access point™ for customer coll.",
        "Delivered",
        "Delivered ",
        "Delivered to ups access point™ ",
        "Delivery attempt could not be completed",
        "Delivery attempted but no response at consignee address",
        "Delivery attempted – consignee premises closed",
        "Delivery not accepted",
        "Out for delivery",
        "Out for delivery today",
        "Shipment is out with courier for delivery",
    }

    for date, description in data:
        if description in deliveredStatuses:
            return (datetime.datetime.strptime(date, "%Y-%m-%d"), description)

    return data[-1]  # If no matching tuple is found


# Function to check the next working day, skipping weekends and holidays
def next_working_day(current_date, daystoadd=1):
    next_day = current_date
    while daystoadd > 0:
        next_day += datetime.timedelta(days=1)
        if (
            next_day.weekday() < 5
            and next_day.strftime("%Y-%m-%d") not in holiday_dates
        ):
            daystoadd -= 1
    return next_day


def check_shipping_status(self):
    try:
        if self.ol_state == 2:
            return "Awaiting Shipment"

        if self.ol_state in [4, 5]:
            return "Cancelled"

        # Assuming date_creation and date_shipping are datetime objects
        date_creation = self.date_creation

        date_shipping = self.date_shipping

        last_shipping_update = parse_date(self.history[-1][0])

        day_of_week = date_creation.weekday()
        time_of_day = date_creation.time()
        delivery_status = find_first_delivery_attempt(self.history)[1]
        delivery_date = find_first_delivery_attempt(self.history)[0]

        if time_of_day < datetime.time(14, 0, 0):  # 14:00:00
            if day_of_week in [5, 6]:  # Saturday or Sunday
                expected_shipping_date = next_working_day(date_creation)
            else:
                expected_shipping_date = date_creation
        else:
            expected_shipping_date = next_working_day(date_creation)

        # Check if the expected shipping day is a holiday, then skip to the next working day
        while expected_shipping_date.strftime("%Y-%m-%d") in holiday_dates:
            expected_shipping_date = next_working_day(expected_shipping_date)

        expected_arrival = next_working_day(expected_shipping_date, daystoadd=2)

        # Check if the expected shipping day is a holiday, then skip to the next working day
        while expected_arrival.strftime("%Y-%m-%d") in holiday_dates:
            expected_arrival = next_working_day(expected_shipping_date)

        if date_shipping:
            if delivery_status in deliveredStatuses:
                if delivery_date.date() <= expected_arrival.date():
                    return "On Time"
                else:
                    return "Late to the Party"
            else:
                if last_shipping_update.date() <= expected_arrival.date():
                    return "Not Arrived"
                else:
                    return "Overdue"
        else:
            return "Not Shipped"
    except:
        print(traceback.format_exc())
        return "Error with Shipping Info"
