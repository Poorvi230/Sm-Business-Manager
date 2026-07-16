from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

inventory_db = [
    {"id": 1, "name": "Office Chair", "quantity": 15, "price": 120.00},
    {"id": 2, "name": "MacBook Pro", "quantity": 4, "price": 1500.00}
]

@app.route('/')
def home():
    return render_template('index.html')

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
    
    return render_template('inventory.html', items=inventory_db)

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
        total_pay = regular_pay + overtime_pay

        pay_stub = {
            "name": emp_name,
            "regular_pay": round(regular_pay, 2),
            "overtime_pay": round(overtime_pay, 2),
            "total_pay": round(total_pay, 2)
        }

    return render_template('payroll.html', stub=pay_stub)

if __name__== '__main__':
    app.run(debug=True)
    