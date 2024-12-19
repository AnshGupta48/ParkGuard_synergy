import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
import random
import mysql.connector
from datetime import datetime, timedelta
import qrcode
from PIL import Image, ImageTk 

db = mysql.connector.connect(
    host="localhost",        
    user="root",            
    password="mysqlanshanu.2021",  
    database="ParkingSystem"
)
cursor = db.cursor()

def check_availability():
    cursor.execute("SELECT slot_id FROM ParkingSlots WHERE status = 'vacant'")
    vacant_slots = cursor.fetchall()
    return vacant_slots

def create_ticket():
    vehicle_number = vehicle_number_entry.get()
    vacant_slots = check_availability()
    if vacant_slots:
        ticket_id = "TICKET" + str(random.randint(1000, 9999))
        slot_id = vacant_slots[0][0]  # Get first available slot
        expiry_time = datetime.now() + timedelta(hours=2)
        
        cursor.execute(
            "INSERT INTO Tickets (ticket_id, slot_id, vehicle_number, status, expiry_time) VALUES (%s, %s, %s, %s, %s)",
            (ticket_id, slot_id, vehicle_number, 'active', expiry_time)
        )
        db.commit()
        
        cursor.execute("UPDATE ParkingSlots SET status = %s WHERE slot_id = %s", ("occupied", slot_id))
        db.commit()
        
        generate_qr_code(ticket_id)
        
        messagebox.showinfo("Ticket Created", f"Ticket created for vehicle {vehicle_number}. Expiry Time: {expiry_time}")
    else:
        messagebox.showwarning("No Slots", "No available parking slots.")

def generate_qr_code(ticket_id):
    qr = qrcode.make(ticket_id)
    qr.save(f"{ticket_id}.png")

def validate_ticket():
    ticket_id = ticket_id_entry.get()
    cursor.execute("SELECT * FROM Tickets WHERE ticket_id = %s", (ticket_id,))
    ticket = cursor.fetchone()
    
    if ticket:
        ticket_id, slot_id, vehicle_number, status, expiry_time = ticket
        if status == 'active' and datetime.now() < expiry_time:
            messagebox.showinfo("Ticket Valid", f"Ticket {ticket_id} is valid. Vehicle: {vehicle_number}, Slot: {slot_id}")
        else:
            messagebox.showwarning("Invalid Ticket", f"Ticket {ticket_id} is either expired or invalid.")
            cursor.execute("UPDATE Tickets SET status = %s WHERE ticket_id = %s", ('expired', ticket_id))
            db.commit()
            cursor.execute("UPDATE ParkingSlots SET status = %s WHERE slot_id = %s", ("vacant", slot_id))
            db.commit()
    else:
        messagebox.showwarning("Ticket Not Found", f"Ticket {ticket_id} not found.")

def exit_app():
    cursor.close()
    db.close()
    root.quit()

root = tk.Tk()
root.title("Parking System")
root.geometry("700x500")  
root.configure(bg="#f4f4f9")  
custom_font = tkfont.Font(family="Helvetica", size=12)
button_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
vehicle_frame = tk.Frame(root, bg="#f4f4f9")
vehicle_frame.pack(pady=20)

vehicle_number_label = tk.Label(vehicle_frame, text="Enter Vehicle Number:", font=custom_font, bg="#f4f4f9")
vehicle_number_label.grid(row=0, column=0, padx=10)

vehicle_number_entry = tk.Entry(vehicle_frame, font=custom_font, width=20, bd=2, relief="solid", highlightthickness=1)
vehicle_number_entry.grid(row=0, column=1, padx=10)

action_frame = tk.Frame(root, bg="#f4f4f9")
action_frame.pack(pady=30)

check_button = tk.Button(action_frame, text="Check Parking Availability", command=lambda: check_availability(), font=button_font, bg="#4CAF50", fg="white", width=20, height=2, relief="flat")
check_button.grid(row=0, column=0, padx=10, pady=10)

issue_ticket_button = tk.Button(action_frame, text="Issue Ticket", command=create_ticket, font=button_font, bg="#4CAF50", fg="white", width=20, height=2, relief="flat")
issue_ticket_button.grid(row=1, column=0, padx=10, pady=10)

ticket_id_label = tk.Label(action_frame, text="Enter Ticket ID to Validate:", font=custom_font, bg="#f4f4f9")
ticket_id_label.grid(row=2, column=0, padx=10)

ticket_id_entry = tk.Entry(action_frame, font=custom_font, width=20, bd=2, relief="solid", highlightthickness=1)
ticket_id_entry.grid(row=2, column=1, padx=10)

validate_ticket_button = tk.Button(action_frame, text="Validate Ticket", command=validate_ticket, font=button_font, bg="#008CBA", fg="white", width=20, height=2, relief="flat")
validate_ticket_button.grid(row=3, column=0, padx=10, pady=10)

exit_button = tk.Button(root, text="Exit", command=exit_app, font=button_font, bg="#f44336", fg="white", width=20, height=2, relief="flat")
exit_button.pack(pady=20)

def display_qr_code_image(ticket_id):
    qr_image = Image.open(f"{ticket_id}.png")
    qr_image = qr_image.resize((150, 150), Image.ANTIALIAS)
    qr_image = ImageTk.PhotoImage(qr_image)
    qr_image_label.config(image=qr_image)
    qr_image_label.image = qr_image

qr_image_label = tk.Label(root)
qr_image_label.pack(pady=10)

root.mainloop()