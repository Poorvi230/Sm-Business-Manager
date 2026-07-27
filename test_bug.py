import json

DB_FILE = 'business_data.json'
with open(DB_FILE, 'r') as file:
    app_data = json.load(file)

inventory_db = app_data["inventory"]
payroll_db = app_data["payroll"]
crm_db = app_data["crm"]
customers_db = app_data.get("customers", [])

def save_db():
    data = {"inventory": inventory_db, "payroll": payroll_db, "crm": crm_db, "customers": customers_db }
    with open(DB_FILE, 'w') as file:
        json.dump(data, file, indent=4)

save_db()
print("Success!")
