# Run the Cloud SQL Proxy command in a new PowerShell window
$cloudSqlProxyCommand = "./cloud-sql-proxyPC.exe elite-inn-inventory:europe-west1:eliteinventory"
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", $cloudSqlProxyCommand

# Navigate to the project directory
cd ./elite_inventory

# Activate the Python virtual environment
& 'C:\Users\davet\Documents\GitHub\Elite_Code\Elite_Inventory\venv\Scripts\Activate.ps1'

# Start the Django development server
python manage.py runserver

