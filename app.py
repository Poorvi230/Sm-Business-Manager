from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = "super_secret_business_key"

# --database---
DB_FILE = 'business_data.json'

def load_db():
    if not os.path.exists(DB_FILE):
        return {"inventory": [], "payroll": [], "crm": [], "customers": []}
    with open(DB_FILE, 'r') as file:
        return json.load(file)

def save_db():
    data = {"inventory": inventory_db, "payroll": payroll_db, "crm": crm_db, "customers": customers_db }
    with open(DB_FILE, 'w') as file:
        json.dump(data, file, indent=4)

app_data = load_db()
inventory_db = app_data["inventory"]
payroll_db = app_data["payroll"]
crm_db = app_data["crm"]
customers_db = app_data.get("customers", [])
order_db = []

def get_brand():
    industry = session.get('industry', 'default')
    if industry == 'coffee':
        return {"name": "Midnight Coffee", "color": "#4A2C2A", "theme": "theme-coffee", "inv_placeholder": "Coffee Beans / Syrups"}
    elif industry == 'clothing':
        return {"name": "Thread & Co.", "color": "#D4AF37", "theme": "theme-clothing", "inv_placeholder": "Garment / Size"}
    elif industry == 'tech':
        return {"name": "Nexus Techies", "color": "#00FF41", "theme": "theme-tech", "inv_placeholder": "Hardware / Licenses"}
    else:
        return {"name": "Operations Dashboard", "color": "#111111", "theme": "theme-default", "inv_placeholder": "General Item Name"}

@app.route('/')
def home():
    new_industry = request.args.get('industry')
    if new_industry:
        session['industry'] = new_industry
        return redirect(url_for('home'))

    vault_value = 0
    for item in inventory_db:
        vault_value += item['price'] * item['quantity']

    total_payroll = 0
    for stub in payroll_db:
        total_payroll += stub['net_pay']

    open_tickets = 0
    for ticket in crm_db:
        if ticket['status'] == 'Open':
            open_tickets += 1

    total_revenue = 0
    for order in order_db:
        total_revenue += order['revenue']

    revenue_target = 1000.0
    if total_revenue >= revenue_target:
        progress_percent = 100
    else:
        progress_percent = int((total_revenue / revenue_target) * 100)

    stats = {
        "vault_value": round(vault_value, 2),
        "payroll_total": round(total_payroll, 2),
        "open_tickets": open_tickets,
        "revenue": round(total_revenue, 2),
        "progress": progress_percent,
        "target": revenue_target
    }

    return render_template('index.html', brand=get_brand(), stats=stats)

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if request.method == 'POST':
        new_name = request.form.get('item_name')
        new_qty = request.form.get('item_qty')
        new_price = request.form.get('item_price')

        new_item = {
            "id": len(inventory_db) + 1, "name": new_name, "quantity": int(new_qty), "price": float(new_price)
        }
        inventory_db.append(new_item)
        save_db()

        flash(f"Added {new_qty} x {new_name} to the Vault!")

        return redirect(url_for('inventory'))

    return render_template('inventory.html', items=inventory_db, brand=get_brand())

@app.route('/delete/<int:item_id>')
def delete_item(item_id):

    inventory_db[:] = [item for item in inventory_db if item['id'] != item_id]
    save_db()

    flash("Item permanently deleted.")
    return redirect(url_for('inventory'))

@app.route('/payroll', methods=['GET', 'POST'])
def payroll():
    if request.method == 'POST':
        emp_name = request.form.get('emp_name')
        rate = float(request.form.get('rate'))
        hours = float(request.form.get('hours'))

        regular_hours = min(hours, 40)
        overtime_hours = max(hours - 40, 0)

        regular_pay = regular_hours * rate
        overtime_pay = overtime_hours * (rate * 1.5)
        gross_pay = regular_pay + overtime_pay
        estimated_tax = gross_pay * 0.15
        net_pay = gross_pay - estimated_tax

        pay_stub = {
            "id": len(payroll_db) + 1,
            "name": emp_name,
            "net_pay": round(net_pay, 2),
            "overtime_pay": round(overtime_pay, 2),
            "tax": round(estimated_tax, 2),
            "net_pay": round(net_pay, 2)
        }
        payroll_db.append(pay_stub)
        save_db() 
        return redirect(url_for('payroll'))

    return render_template('payroll.html', history=payroll_db,
brand=get_brand())

# ---client relstion---
@app.route('/crm', methods=['GET', 'POST'])
def crm():
    if request.method == 'POST':
        new_customer = request.form.get('customer_name')
        new_issue = request.form.get('issue_desc')

        new_ticket = {
            "id": len(crm_db) + 1,
            "customer": new_customer,
            "issue": new_issue,
            "status": "Open"
        }
        crm_db.append(new_ticket)
        save_db()
        return redirect(url_for('crm'))

    return render_template('crm.html', tickets=crm_db, brand=get_brand())

@app.route('/resolve/<int:ticket_id>')
def resolve_ticket(ticket_id):
    for ticket in crm_db:
        if ticket['id'] == ticket_id:
            ticket['status'] = 'Resolved'
    save_db()

    flash("Drama resolved! chill")
    return redirect(url_for('crm'))

@app.route('/print_stub/<int:stub_id>')
def print_stub(stub_id):
    target_stub = None
    for stub in payroll_db:
        if stub['id'] == stub_id:
            target_stub = stub
            break

    if not target_stub:
        return redirect(url_for('payroll'))
    
    return render_template('receipt.html', stub=target_stub, brand=get_brand())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        item_id = int(request.form.get('item_id'))
        qty_sold = int(request.form.get('qty_sold'))

        for item in inventory_db:
            if item['id'] == item_id:
                if item['quantity'] >= qty_sold:
                    item['quantity'] -= qty_sold

                    revenue = item['price'] * qty_sold
                    order_db.append({"item": item['name'], "qty": qty_sold, "revenue": revenue})

                    save_db()
                    flash(f"Cha-Ching! Sold {qty_sold} x {item['name']} for ${revenue}!")
                else:
                    flash(f"{item['name']} in vault is dried up 🥀")

                return redirect(url_for('register'))
    return render_template('register.html', items=inventory_db, orders=order_db, brand=get_brand())              

@app.route('/restock/<int:item_id>/<action>')
def restock_item(item_id, action):
    for item in inventory_db:
        if item['id'] == item_id:
            if action == 'add':
                item['quantity'] += 1
            elif action == 'sub' and item['quantity'] > 0:
                item['quantity'] -= 1
    save_db()
    return redirect(url_for('inventory'))  

if __name__ == '__main__':
    app.run(debug=True)
              