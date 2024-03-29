#!/bin/zsh

# Assuming cloud_sql_proxy is already executable and in your PATH
# or adjust the path to where your cloud_sql_proxy binary is located.
cloudSqlProxyCommand="./cloud-sql-proxy --port 5432 elite-inn-inventory:europe-west1:eliteinventory &"
eval $cloudSqlProxyCommand

# Navigate to the project directory
cd ./elite_inventory

# Activate the Python virtual environment
# Adjust the path to the activate script according to where your virtual environment is located.
source '/Users/davidtate/Documents/Code/Work/Inventory_App/venv/bin/activate'

# Start the Django development server
python manage.py runserver
