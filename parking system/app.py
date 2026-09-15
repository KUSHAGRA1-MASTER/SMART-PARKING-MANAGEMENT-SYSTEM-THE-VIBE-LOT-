from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import re

app = Flask(__name__)
DB = "parking.db"

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # 1. Create slots table
    c.execute("""
        CREATE TABLE IF NOT EXISTS slots(
            id INTEGER PRIMARY KEY,
            status TEXT,
            vehicle TEXT,
            type TEXT DEFAULT 'Four-Wheeler'
        )
    """)
    
    # 2. Create history table
    c.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            vehicle TEXT,
            slot INTEGER,
            entry TEXT,
            exit TEXT,
            fee INTEGER,
            plan_type TEXT DEFAULT 'hourly'
        )
    """)

    # 3. Check and add missing columns dynamically
    c.execute("PRAGMA table_info(slots)")
    slot_cols = [col[1] for col in c.fetchall()]
    if 'type' not in slot_cols:
        c.execute("ALTER TABLE slots ADD COLUMN type TEXT DEFAULT 'Four-Wheeler'")
        c.execute("UPDATE slots SET type='Two-Wheeler' WHERE id IN (9, 10)")

    c.execute("PRAGMA table_info(history)")
    history_cols = [col[1] for col in c.fetchall()]
    if 'plan_type' not in history_cols:
        c.execute("ALTER TABLE history ADD COLUMN plan_type TEXT DEFAULT 'hourly'")

    # 4. Populate default slots if table is empty
    count_row = c.execute("SELECT COUNT(*) FROM slots").fetchone()
    if count_row and count_row[0] == 0:
        for i in range(1, 11):
            slot_type = 'Two-Wheeler' if i in [9, 10] else 'Four-Wheeler'
            c.execute("INSERT INTO slots(id, status, vehicle, type) VALUES(?, ?, ?, ?)", (i, "Available", "", slot_type))

    # 5. Commit changes and close connection at the VERY END
    conn.commit()
    conn.close()

# ---------------- ROUTE: DASHBOARD ----------------
@app.route('/')
def home():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    slots = conn.execute("SELECT * FROM slots").fetchall()
    
    available_row = conn.execute("SELECT COUNT(*) FROM slots WHERE status='Available'").fetchone()
    available = available_row[0] if available_row else 0
    occupied = 10 - available
    
    active_vehicles = conn.execute("SELECT * FROM history WHERE exit='' OR exit IS NULL").fetchall()
    history_records = conn.execute("SELECT * FROM history ORDER BY id DESC").fetchall()
    
    conn.close()
    return render_template(
        'index.html', 
        slots=slots, 
        available=available, 
        occupied=occupied, 
        active_vehicles=active_vehicles, 
        history_records=history_records
    )

# ---------------- ROUTE: BOOK SLOT ----------------
@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone'].strip()
        vehicle = request.form['vehicle'].upper().strip().replace(" ", "").replace("-", "")
        plan_type = request.form.get('plan_type', 'hourly')
        vehicle_type = request.form.get('vehicle_type', 'Four-Wheeler')

        if not re.match(r"^[0-9]{10}$", phone):
            return render_template('book.html', error="Invalid Phone Number! Must be exactly 10 digits.")

        rto_pattern = r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$"
        rto_fallback_pattern = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$"

        if not re.match(rto_pattern, vehicle) and not re.match(rto_fallback_pattern, vehicle):
            return render_template('book.html', error=f"Format Error: '{vehicle}' does not match standard Indian RTO layouts. Example: DL3CA1234")

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        
        if vehicle_type == 'Two-Wheeler':
            slot = c.execute("SELECT id FROM slots WHERE status='Available' AND type='Two-Wheeler' LIMIT 1").fetchone()
            if not slot:
                slot = c.execute("SELECT id FROM slots WHERE status='Available' LIMIT 1").fetchone()
        else:
            slot = c.execute("SELECT id FROM slots WHERE status='Available' AND type='Four-Wheeler' LIMIT 1").fetchone()
            if not slot:
                slot = c.execute("SELECT id FROM slots WHERE status='Available' LIMIT 1").fetchone()

        if slot:
            slot_id = slot[0]
            c.execute("UPDATE slots SET status='Occupied', vehicle=? WHERE id=?", (vehicle, slot_id))
            c.execute("""
                INSERT INTO history (name, phone, vehicle, slot, entry, exit, fee, plan_type) 
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, phone, vehicle, slot_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '', 0, plan_type))
            conn.commit()
            conn.close()
            return redirect('/')
        else:
            conn.close()
            return render_template('book.html', error="No matching parking slots available!")
        
    return render_template('book.html')

# ---------------- ROUTE: ACTIVE TRACKING (ADMIN) ----------------
@app.route('/admin')
def admin():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    vehicles = conn.execute("SELECT * FROM history WHERE exit='' OR exit IS NULL").fetchall()
    conn.close()
    return render_template('admin.html', vehicles=vehicles)

# ---------------- ROUTE: BILLING & CHECKOUT (EXIT) ----------------
@app.route('/exit/<int:id>')
def exit_vehicle(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    row = c.execute("SELECT slot, entry, plan_type FROM history WHERE id=?", (id,)).fetchone()
    
    if row:
        slot, entry_str, plan_type = row[0], row[1], row[2]
        entry = datetime.strptime(entry_str, '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        
        is_two_wheeler = (slot in [9, 10])

        if plan_type == 'monthly':
            fee = 300 if is_two_wheeler else 1000  # ₹300/mo for Two-Wheeler, ₹1000/mo for Four-Wheeler
        else:
            duration = now - entry
            hours = (duration.total_seconds() // 3600) + 1
            hourly_rate = 5 if is_two_wheeler else 10
            base_fee = 10 if is_two_wheeler else 20
            fee = int(base_fee + max(0, hours - 1) * hourly_rate)

        c.execute("UPDATE slots SET status='Available', vehicle='' WHERE id=?", (slot,))
        c.execute("UPDATE history SET exit=?, fee=? WHERE id=?", (now.strftime('%Y-%m-%d %H:%M:%S'), fee, id))
        conn.commit()
        
    conn.close()
    return redirect('/history-log')

# ---------------- ROUTE: SYSTEM ARCHIVE LOG ----------------
@app.route('/history-log')
def history_log():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    past_records = conn.execute("SELECT * FROM history WHERE exit != '' ORDER BY exit DESC").fetchall()
    
    revenue_row = conn.execute("SELECT SUM(fee) FROM history").fetchone()
    total_revenue = revenue_row[0] if revenue_row and revenue_row[0] is not None else 0
    
    conn.close()
    return render_template('history_log.html', records=past_records, revenue=total_revenue)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)