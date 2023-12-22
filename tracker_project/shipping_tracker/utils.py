import datetime
import requests
import traceback

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
