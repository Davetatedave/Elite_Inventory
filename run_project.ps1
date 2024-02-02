# Run the Cloud SQL Proxy command in a new PowerShell window
$cloudSqlProxyCommand = "./cloud-sql-proxy.exe elite-innovations-cloud:us-central1:eliteinventory"
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", $cloudSqlProxyCommand

# Navigate to the project directory
cd ./tracker_project

# Activate the Python virtual environment
& 'C:\Users\davet\Documents\GitHub\Elite_Code\Shipment_Tracker\venv\Scripts\Activate.ps1'

# Start the Django development server
python manage.py runserver

