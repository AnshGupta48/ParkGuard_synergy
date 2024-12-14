import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysqlanshanu.2021",  
    database="ParkingSystem"
)

cursor = db.cursor()

insert_query = "INSERT INTO ParkingSlots (status, location) VALUES (%s, %s)"

values = [(f'vacant', f'Floor {(i // 100) + 1}') for i in range(1, 1001)]

cursor.executemany(insert_query, values)
db.commit()

print(f"Inserted {cursor.rowcount} rows into ParkingSlots.")

cursor.close()
db.close()
