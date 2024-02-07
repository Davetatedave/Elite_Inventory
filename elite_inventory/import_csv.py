import csv
import django
import os

# Set the DJANGO_SETTINGS_MODULE environment variable to your project's settings module.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory_project.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# Call django.setup() to configure the Django environment.
django.setup()

from inventory.models import deviceAttributes

with open("../skusntha.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    added = 0
    count = 0
    device_count = deviceAttributes.objects.count()
    print(f"Total devices: {device_count}")
    for row in reader:
        count += 1
        try:
            deviceAttributes.objects.create(
                sku=row["SKU"],
                manufacturer="Apple",
                model=row["Model"],
                color=row["Color"],
                capacity=row["Size"],
                carrier="None",
                grade=row["Condition"],
            )
            added += 1
        except Exception as e:
            print(e)

    print(f"Devices Added:{added}/{count}")
