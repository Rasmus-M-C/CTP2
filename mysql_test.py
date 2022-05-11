import mysql.connector
import mysql
from datetime import datetime
now = datetime.now()
formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

#establishing the connection
conn = mysql.connector.connect(
   user='dokkedalleth_dk', password='kodeord1234', host='mysql23.unoeuro.com', database='dokkedalleth_dk_db_events')

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

# Preparing SQL query to INSERT a record into the database.
insert_stmt = ("INSERT INTO sensordata (device_id, device_type, measurement, timestamp)"
   "VALUES (%s, %s, %s, %s)"
)

data = (str('5'),str('pir_sensor'), str('true'), formatted_date)

   # Executing the SQL command
cursor.execute(insert_stmt, data)

   # Commit your changes in the database
conn.commit()



# Closing the connection
conn.close()