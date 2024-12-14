from flask import Flask, render_template, request, jsonify
import mysql.connector
import random
from datetime import datetime, timedelta
import qrcode
import os
app = Flask(__name__)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysqlanshanu.2021",
    database="ParkingSystem"
)
cursor = db.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_availability', methods=['GET'])
def check_availability():
    cursor.execute("SELECT slot_id FROM ParkingSlots WHERE status = 'vacant'")
    vacant_slots = cursor.fetchall()
    if vacant_slots:
        return jsonify({"status": "success", "slot_id": vacant_slots[0][0]})
    return jsonify({"status": "error", "message": "No available slots."})

@app.route('/create_ticket', methods=['POST'])
def create_ticket():
    vehicle_number = request.form.get('vehicle_number')
    if not vehicle_number:
        return jsonify({"status": "error", "message": "Vehicle number is required!"})

    cursor.execute("SELECT slot_id FROM ParkingSlots WHERE status = 'vacant' LIMIT 1")
    vacant_slot = cursor.fetchone()
    
    if vacant_slot:
        slot_id = vacant_slot[0]
        ticket_id = "TICKET" + str(random.randint(1000, 9999))
        expiry_time = datetime.now() + timedelta(hours=2)

        cursor.execute(
            "INSERT INTO Tickets (ticket_id, slot_id, vehicle_number, status, expiry_time) VALUES (%s, %s, %s, %s, %s)",
            (ticket_id, slot_id, vehicle_number, 'active', expiry_time)
        )
        db.commit()

        cursor.execute("UPDATE ParkingSlots SET status = 'occupied' WHERE slot_id = %s", (slot_id,))
        db.commit()

        qr = qrcode.make(ticket_id)
        qr_path = os.path.join('static', 'images', f"{ticket_id}.png")
        qr.save(qr_path)

        return jsonify({"status": "success", "ticket_id": ticket_id, "expiry_time": expiry_time, "qr_code": qr_path})
    else:
        return jsonify({"status": "error", "message": "No available parking slots."})

if __name__ == '__main__':
    app.run(debug=True)
