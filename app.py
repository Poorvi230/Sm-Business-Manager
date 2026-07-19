from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_business_key" 

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
            
            return render_template('index.html', brand=get_brand())


crm_db = [
    {"id": 1, "customer": "John Doe", "issue": "Late delivery", "status": "Open"},
    {"id": 2, "customer": "Sarah Smith", "issue": "Wrong item received", "status": "Resolved"}
]
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
        return redirect(url_for('crm'))
    return render_template('crm.html', tickets=crm_db, brand=get_brand())

#--inventory's road--
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

        return redirect(url_for('inventory'))
    
    return render_template('inventory.html', items=inventory_db, brand=get_brand())

@app.route('/payroll', methods=['GET', 'POST'])
def payroll():
    pay_stub = None 
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
            "name": emp_name,
            "regular_pay": round(regular_pay, 2),
            "overtime_pay": round(overtime_pay, 2),
            "gross_pay": round(gross_pay, 2),
            "tax": round(estimated_tax, 2),
            "net_pay": round(net_pay, 2)
        }

    return render_template('payroll.html', stub=pay_stub, brand=get_brand())

if __name__== '__main__':
    app.run(debug=True)

