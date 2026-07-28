from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = "super_secret_business_key"

DB_FILE = 'business_data.json'


def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as file:
                return json.load(file)
        except Exception:
            pass
    return {"inventory": [], "payroll": [], "crm": [], "customers": [], "revenue": 0, "orders": []}


def save_db():
    data = {
        "inventory": inventory_db,
        "payroll": payroll_db,
        "crm": crm_db,
        "customers": customers_db,
        "revenue": revenue,
        "orders": order_db
    }
    with open(DB_FILE, 'w') as file:
        json.dump(data, file, indent=4)


app_data = load_db()
if not isinstance(app_data, dict):
    print("app_data came back weird (not a dict), resetting to empty db")
    app_data = {"inventory": [], "payroll": [], "crm": [], "customers": [], "revenue": 0, "orders": []}

inventory_db = app_data.get("inventory", [])
payroll_db = app_data.get("payroll", [])
crm_db = app_data.get("crm", [])
customers_db = app_data.get("customers", [])
revenue = app_data.get("revenue", 0)
order_db = app_data.get("orders", [])


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

    vault_value = sum(item['price'] * item['quantity'] for item in inventory_db)
    total_payroll = sum(stub.get('net_pay', 0) for stub in payroll_db)
    pending_tickets = sum(1 for ticket in crm_db if ticket.get('status') == 'Open')
    total_customers = len(customers_db)

    goal = 10000.0
    progress_percentage = min((revenue / goal) * 100, 100)

    stats = {
        "vault_value": round(vault_value, 2),
        "payroll_total": round(total_payroll, 2),
        "open_tickets": pending_tickets,
        "revenue": round(revenue, 2),
        "progress": progress_percentage,
        "target": goal
    }

    brand = get_brand()

    return render_template('index.html', brand=brand, stats=stats)


@app.route('/inventory', methods=['GET', 'POST'])
def vault():
    global inventory_db
    brand = get_brand()

    if request.method == 'POST':
        name = request.form.get('item_name')
        price = float(request.form.get('item_price', 0))
        quantity = int(request.form.get('item_qty', 0))

        new_id = max([item['id'] for item in inventory_db], default=0) + 1
        inventory_db.append({
            "id": new_id,
            "name": name,
            "price": price,
            "quantity": quantity
        })
        save_db()
        flash(f"Successfully added {name} to inventory!", "success")
        return redirect(url_for('vault'))

    return render_template('inventory.html', brand=brand, items=inventory_db)

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    global inventory_db
    inventory_db[:] = [item for item in inventory_db if item['id'] != item_id]
    save_db()
    flash("Item permanently deleted.", "success")
    return redirect(url_for('vault'))


@app.route('/restock/<int:item_id>/<string:action>')
def adjust_stock(item_id, action):
    global inventory_db
    for item in inventory_db:
        if item['id'] == item_id:
            if action in ['add', 'increase', 'plus']:
                item['quantity'] += 1
            elif action in ['remove', 'decrease', 'sub', 'minus'] and item['quantity'] > 0:
                item['quantity'] -= 1
            break
    save_db()
    return redirect(url_for('vault'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    global inventory_db, revenue, customers_db
    brand = get_brand()

    if request.method == 'POST':
        item_id = int(request.form.get('item_id', 0))
        customer_name = request.form.get('customer_name', 'Guest')
        quantity = int(request.form.get('qty_sold', 1))

        selected_item = next((item for item in inventory_db if item['id'] == item_id), None)

        if selected_item:
            if selected_item['quantity'] >= quantity:
                selected_item['quantity'] -= quantity
                sale_amount = selected_item['price'] * quantity
                revenue += sale_amount

                customer_found = False
                for c in customers_db:
                    if c['name'].lower() == customer_name.lower():
                        c['total_spent'] += sale_amount
                        customer_found = True
                        break

                if not customer_found:
                    customers_db.append({
                        "name": customer_name,
                        "total_spent": sale_amount
                    })

                order_db.append({"item": selected_item['name'], "qty": quantity, "revenue": sale_amount})
                save_db()
                flash(f"Sold {quantity}x {selected_item['name']}! +${sale_amount} secured.", "success")
            else:
                flash("Not enough stock left in the vault!", "error")

        return redirect(url_for('register'))

    return render_template('register.html', brand=brand, items=inventory_db, customers=customers_db, orders=order_db)


@app.route('/payroll', methods=['GET', 'POST'])
def payroll():
    global payroll_db
    brand = get_brand()

    if request.method == 'POST':
        name = request.form.get('emp_name')
        hours = float(request.form.get('hours', 0))
        rate = float(request.form.get('rate', 0))
        bonus = float(request.form.get('bonus', 0))
        net_pay = (hours * rate) + bonus

        new_id = max([stub['id'] for stub in payroll_db], default=0) + 1
        payroll_db.append({
            "id": new_id,
            "name": name,
            "hours": hours,
            "rate": rate,
            "bonus": bonus,
            "net_pay": net_pay
        })
        save_db()
        flash(f"Logged pay stub for {name}! Net: ${net_pay}", "success")
        return redirect(url_for('payroll'))

    return render_template('payroll.html', brand=brand, history=payroll_db)


@app.route('/print_stub/<int:stub_id>')
def print_receipt(stub_id):
    brand = get_brand()
    stub = next((s for s in payroll_db if s['id'] == stub_id), None)
    if not stub:
        flash("Pay stub not found!", "error")
        return redirect(url_for('payroll'))
    return render_template('receipt.html', brand=brand, stub=stub)


@app.route('/crm', methods=['GET', 'POST'])
def crm():
    global crm_db
    brand = get_brand()

    if request.method == 'POST':
        customer = request.form.get('customer_name')
        complaint = request.form.get('issue_desc')

        new_id = max([t['id'] for t in crm_db], default=0) + 1
        crm_db.append({
            "id": new_id,
            "customer": customer,
            "issue": complaint,
            "status": "Open"
        })
        save_db()
        flash("Logged the issue! We will deal with it.", "success")
        return redirect(url_for('crm'))

    return render_template('crm.html', brand=brand, tickets=crm_db)


@app.route('/resolve/<int:ticket_id>')
def resolve_ticket(ticket_id):
    global crm_db
    for ticket in crm_db:
        if ticket['id'] == ticket_id:
            ticket['status'] = 'Resolved'
            break
    save_db()
    flash("Ticket resolved!", "success")
    return redirect(url_for('crm'))


@app.route('/rolodex')
def customers():
    brand = get_brand()
    whales = sorted(customers_db, key=lambda x: x.get('total_spent', 0), reverse=True)
    return render_template('rolodex.html', brand=brand, customers=whales)


if __name__ == '__main__':
    app.run(debug=True)
