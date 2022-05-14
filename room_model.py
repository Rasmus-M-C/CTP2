from dataclasses import dataclass
import json
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish, subscribe
from time import sleep, time
import mysql.connector
import mysql
import test
from datetime import datetime

sensor_list = ["SENSOR1"]
@dataclass
class Room():
  Id_sensor: str
  Id_LED: str
  Previous_room_visited: bool
  Room_visisted: bool
  Next_room_visited: bool
  Host: str
  Port: int
  Internal_counter: int = 0

  def __init__(self,id_sensor, id_LED, previous_room_visited, Room_visisted, next_room_visited, Host, Port):
    self.Id_sensor = id_sensor
    self.Id_LED = id_LED
    self.Previous_room_visited = previous_room_visited
    self.Room_visisted = Room_visisted
    self.Next_room_visited = next_room_visited
    self.Host = Host
    self.Port = Port
  #Methods 

@dataclass
class Server():
  password: str
  user: str
  db_name: str
  host_server: str
  mysql_conn : mysql.connector

  def __init__(self, user, password, host_server, db_name):
    self.user = user
    self.password = password
    self.db_name = db_name
    self.host_server = host_server
    self.mysql_conn = mysql.connector.connect(
    host=self.host_server, 
    user=self.user, 
    password=self.password, 
    database = self.db_name)

  def store_sensor_event(self, room_id: int):
    mysql_conn = mysql.connector.connect(user = self.user, password = self.password, host = self.host_server, database = self.db_name)
    
    #mysql_conn = mysql.connector.connect(user=self.user, password=self.password, host=self.host_server, database=self.db_name)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S') # Current time in SQL format
    
    cursor = mysql_conn.cursor()
    insert_stmt = ("INSERT INTO sensordata (room_id, device_type, measurement, timestamp)"
     "VALUES (%s, %s, %s, %s)") ## Table values
    data = (str(room_id),str('PIR Sensor'), str(True), formatted_date)
    cursor.execute(insert_stmt, data)
    mysql_conn.commit()
    print("logged data")
    mysql_conn.close()



@dataclass
class Controller(): # changes model aka rooms
  room_list: list
  MYSQL_Server: Server
  def __init__(self, room_list_input, input_server):
    self.room_list = room_list_input
    self.MYSQL_Server = input_server
  

  def set_room_visited(self, Room, index: int):
    self.room_list[index].Room_visisted = True

  def set_room_not_visited(self, room_list: list, index: int):
    self.room_list[index].Room_visisted = False

    #self.occupied_thread.start()
  def sanitize_message(self, client, userdata, message) -> dict:
    print("in sanitize")
    for sensor in sensor_list:
      print("in for loop")
      if f"{sensor}" in message.topic:  
        print("sensor here")
        payload_recieve = message.payload.decode("utf-8")
        payload_recieve = json.loads(payload_recieve)
        payload_recieve.update ({"SENSOR_ID": sensor.partition("R")[2]})
        room_num_index = int(payload_recieve["SENSOR_ID"]) - 1 
        print (room_num_index)
        print(payload_recieve["occupancy"]=="true")
        if (payload_recieve["occupancy"] == "true"):
          #self.set_room_visited(self, room_list, room_num_index)
          #client.publish(topic=f"zigbee2mqtt/LED{payload_recieve["SENSOR_ID"]}/set", payload=json.dumps({"state": "ON"}))
          client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"state": "OFF"}))
          self.MYSQL_Server.store_sensor_event(room_num_index+1)
        #if (room_list[room_num_index].Internal_counter % 5 == 0 and payload_recieve["occupancy"] == False):
        elif (self.room_list[room_num_index].Internal_counter % 5 == 0):
          client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"state": "ON"}))
          #self.set_room_not_visited(self, self.room_list, room_num_index)
        self.room_list[room_num_index].Internal_counter = self.room_list[room_num_index].Internal_counter + 1
        print(f" interal counter {self.room_list[room_num_index].Internal_counter}")

  def control_loop(self):
    # Create a data model and add a list of known Zigbee devices.
    mqtt_client= MqttClient()
    # Connect to the host given in initializer.
    mqtt_client.connect("127.0.0.1", 1883)
    mqtt_client.on_message = self.sanitize_message
    mqtt_client.loop_start()
    # Subscribe to all topics given in the initializer.
    #mqtt_client.subscribe("zigbee2mqtt/#")
    mqtt_client.subscribe("zigbee2mqtt/#")
    mqtt_client.subscribe("zigbee2mqtt/SENSOR1")
    
    # Start the subscriber thread.
    sleep(3)
    mqtt_client.publish(topic="zigbee2mqtt/SENSOR1", payload=json.dumps({"occupancy": "true"}))
    x = 1
    while True:
      print(f"Waiting ...{x}")
      x = x + 1
      sleep(2)







