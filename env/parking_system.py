import mysql.connector
import qrcode
import random
import cv2
from datetime import datetime, timedelta

db = mysql.connector.connect(
    host="localhost",        
    user="root",            
    password="mysqlanshanu.2021",  
    database="ParkingSystem"  
)

cursor = db.cursor()

def get_parking_slots():
    cursor.execute("SELECT * FROM ParkingSlots")
    slots = cursor.fetchall()
    return slots

def update_parking_slot(slot_id, status):
    cursor.execute("UPDATE ParkingSlots SET status = %s WHERE slot_id = %s", (status, slot_id))
    db.commit()

def create_ticket(ticket_id, slot_id, vehicle_number):
    expiry_time = datetime.now() + timedelta(hours=2)  # Ticket expires in 2 hours
    cursor.execute(
        "INSERT INTO Tickets (ticket_id, slot_id, vehicle_number, status, expiry_time) VALUES (%s, %s, %s, %s, %s)",
        (ticket_id, slot_id, vehicle_number, 'active', expiry_time)
    )
    db.commit()
    print(f"Ticket created for vehicle {vehicle_number}. Expiry Time: {expiry_time}")

def check_availability():
    cursor.execute("SELECT slot_id FROM ParkingSlots WHERE status = 'vacant'")
    vacant_slots = cursor.fetchall()
    return vacant_slots

def generate_qr_code(ticket_id):
    qr = qrcode.make(ticket_id)
    qr.save(f"{ticket_id}.png")

def validate_ticket(ticket_id):
    cursor.execute("SELECT * FROM Tickets WHERE ticket_id = %s", (ticket_id,))
    ticket = cursor.fetchone()

    if ticket:
        ticket_id, slot_id, vehicle_number, status, expiry_time = ticket
        if status == 'active' and datetime.now() < expiry_time:
            print(f"Ticket {ticket_id} is valid. Vehicle: {vehicle_number}, Slot: {slot_id}")
        else:
            print(f"Ticket {ticket_id} is either expired or invalid.")
            update_parking_slot(slot_id, "vacant")
            cursor.execute("UPDATE Tickets SET status = %s WHERE ticket_id = %s", ('expired', ticket_id))
            db.commit()
    else:
        print(f"Ticket {ticket_id} not found.")

def scan_qr_code_and_validate():
    cap = cv2.VideoCapture(0)
    
    print("Scanning QR Code... (Press 'q' to quit)")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        decoded_objects = cv2.detectAndDecode(frame)
        
        for obj in decoded_objects:
            ticket_id = obj
            print(f"Scanned Ticket ID: {ticket_id}")
            validate_ticket(ticket_id)
            break
        
        cv2.imshow("QR Code Scanner", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def menu():
    while True:
        print("\nParking System Menu:")
        print("1. Check Parking Slot Availability")
        print("2. Issue a Parking Ticket")
        print("3. Validate Ticket")
        print("4. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            vacant_slots = check_availability()
            if vacant_slots:
                print("Available Slot:", vacant_slots[0][0])
            else:
                print("No available slots.")
        elif choice == '2':
            vehicle_number = input("Enter vehicle number: ")
            vacant_slots = check_availability()
            if vacant_slots:
                ticket_id = "TICKET" + str(random.randint(1000, 9999))
                create_ticket(ticket_id, vacant_slots[0][0], vehicle_number)
                update_parking_slot(vacant_slots[0][0], "occupied")
                generate_qr_code(ticket_id)
            else:
                print("No available slots.")
        elif choice == '3':
            ticket_id = input("Enter ticket ID for validation: ")
            validate_ticket(ticket_id)
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

vacant_slots = check_availability()
if vacant_slots:
    print("Available slot found:", vacant_slots[0][0])
    ticket_id = "TICKET" + str(random.randint(1000, 9999))
    create_ticket(ticket_id, vacant_slots[0][0], "ABC1234")
    update_parking_slot(vacant_slots[0][0], "occupied")
    generate_qr_code(ticket_id)
    print("Ticket created, and QR code generated.")
else:
    print("No available slots.")

cursor.close()
db.close()
