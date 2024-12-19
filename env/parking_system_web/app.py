from flask import Flask, logging, render_template, request, jsonify, redirect, url_for
import mysql.connector
import random
from datetime import datetime, timedelta
import qrcode
import os
from reportlab.pdfgen import canvas
from PIL import Image, ImageFilter, ImageEnhance
import easyocr
import logging


app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysqlanshanu.2021",
    database="ParkingSystem"
)
cursor = db.cursor()

NGROK_URL = "https://3157-49-36-90-240.ngrok-free.app"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_ticket_page')
def create_ticket_page():
    return render_template('create_ticket.html')

@app.route('/check_availability', methods=['GET'])
def check_availability():
    try:
        cursor.execute("SELECT slot_id FROM ParkingSlots WHERE status = 'vacant'")
        vacant_slots = cursor.fetchall()
        if vacant_slots:
            return jsonify({"status": "success", "slot_id": vacant_slots[0][0]})
        return jsonify({"status": "error", "message": "No available slots."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"})

def extract_vehicle_number_easyocr(image_path):
    reader = easyocr.Reader(['en']) 
    results = reader.readtext(image_path, detail=0)  
    return " ".join(results).strip()

@app.route('/create_ticket', methods=['POST'])
def create_ticket():
    vehicle_number = request.form.get('vehicle_number')
    vehicle_image = request.files.get('vehicle_image')

    if not vehicle_number or not vehicle_image:
        return jsonify({"status": "error", "message": "Vehicle number and image are required!"})

  
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], vehicle_image.filename)
    vehicle_image.save(image_path)

    try:
        extracted_text = extract_vehicle_number_easyocr(image_path)
        logging.info(f"Extracted text: {extracted_text}") 
        if vehicle_number not in extracted_text:
            return jsonify({"status": "error", "message": "License plate does not match the entered vehicle number!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"OCR error: {str(e)}"})

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

        # Update slot status
        cursor.execute("UPDATE ParkingSlots SET status = 'occupied' WHERE slot_id = %s", (slot_id,))
        db.commit()

        qr_data = f"{https://3157-49-36-90-240.ngrok-free.app}/validate_ticket?ticket_id={ticket_id}"
        qr = qrcode.make(qr_data)
        qr_path = os.path.join('static', 'images', f"{ticket_id}.png")
        qr.save(qr_path)

        pdf_path = os.path.join('static', 'tickets', f"{ticket_id}.pdf")
        c = canvas.Canvas(pdf_path)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(200, 750, "Parking Ticket")
        c.setFont("Helvetica", 14)
        c.drawString(50, 700, f"Ticket ID: {ticket_id}")
        c.drawString(50, 670, f"Vehicle Number: {vehicle_number}")
        c.drawString(50, 640, f"Slot ID: {slot_id}")
        c.drawString(50, 610, f"Expiry Time: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawImage(qr_path, 400, 600, width=150, height=150)
        c.save()

        return jsonify({
            "status": "success",
            "ticket_id": ticket_id,
            "expiry_time": expiry_time.strftime('%Y-%m-%d %H:%M:%S'),
            "qr_code": qr_path,
            "ticket_pdf": pdf_path
        })
    else:
        return jsonify({"status": "error", "message": "No available parking slots."})

@app.route('/slot_status', methods=['GET'])
def slot_status():
    try:
        cursor.execute("SELECT slot_id, status, vehicle_number FROM ParkingSlots")
        slots = cursor.fetchall()
        slot_data = [
            {"slot_id": slot[0], "status": slot[1], "vehicle_number": slot[2] if slot[2] else "N/A"}
            for slot in slots
        ]
        return jsonify({"status": "success", "slots": slot_data})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"})

@app.route('/update_slot_status', methods=['POST'])
def update_slot_status():
    slot_id = request.form.get('slot_id')
    new_status = request.form.get('status')
    try:
        cursor.execute("UPDATE ParkingSlots SET status = %s WHERE slot_id = %s", (new_status, slot_id))
        db.commit()
        return jsonify({"status": "success", "message": "Slot status updated successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
