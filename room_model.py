from dataclasses import dataclass
import json
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish, subscribe
from time import sleep, time
import mysql.connector
import mysql
import test
from datetime import datetime
import time


sensor_list = ["SENSOR1", "SENSOR2", "SENSOR3", "SENSOR4", "SENSOR5"]
timing = {"start_time": 0, "time_to_bathroom": 0, "time_in_bathroom": 0, "time_to_bedroom": 0}
    #start tid = Tid_sensor1
    #længde tid bad = Tid_sensor5-Tid_sensor1
    #tid på badeværelse =  Tid_sensor4_anden_gang - Tid_sensor5
    #længde tid soveværelse Tid_sensor1_anden_gang - Tid_sensor4-
@dataclass
class Room():
  Id_sensor: str
  Id_LED: str
  Host: str
  Port: int
  Room_visited: int = 0
  Internal_counter: int = 0

  def __init__(self,id_sensor, id_LED, Host, Port):
    self.Id_sensor = id_sensor
    self.Id_LED = id_LED
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
    
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S') # Current time in SQL format
    
    cursor = self.mysql_conn.cursor()
    insert_stmt = ("INSERT INTO sensordata (room_id, device_type, measurement, timestamp)"
     "VALUES (%s, %s, %s, %s)") ## Table values
    data = (str(room_id),str('PIR Sensor'), str(True), formatted_date)
    cursor.execute(insert_stmt, data)
    self.mysql_conn.commit()
    print("Logged sensor data")
    #self.mysql_conn.close()
  
  def store_bathroom_event(self, timing: dict): 

    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S') # Current time in SQL format
    
    cursor = self.mysql_conn.cursor()
    insert_stmt = ("INSERT INTO bathroom_data (time_to_bathroom, time_in_bathroom, time_to_bedroom, timestamp)"
     "VALUES (%s, %s, %s, %s)") ## Table values
    data = (timing["time_to_bathroom"], timing["time_in_bathroom"], timing["time_to_bedroom"], formatted_date)
    cursor.execute(insert_stmt, data)
    self.mysql_conn.commit()
    print("Logged bathroom event")
    #self.mysql_conn.close()



@dataclass
class Controller(): # changes model aka rooms
  room_list: list
  MYSQL_Server: Server
  def __init__(self, room_list_input, input_server):
    self.room_list = room_list_input
    self.MYSQL_Server = input_server
  
  


  
  ####################################################################################
  ######den udregner time_to_bathroom forkert, time_in_bathroom, time_to_bedroom######
  ####################################################################################
  def bathroom_event(self, room_list: list, timing: dict): ## den udregner time_to_bathroom forkert, time_in_bathroom, time_to_bedroom######
    
    room_list_len = len(room_list)-1
    if(room_list[0].Room_visited - int(time.time()) > room_list[-1].Room_visited - int(time.time()) and room_list[-1].Room_visited): # vi kommer fra soveværelset
      for index, room in enumerate(room_list):
        if(index != room_list_len):
          if(room_list[index].Room_visited != 0 and room_list[index+1].Room_visited - room_list[index].Room_visited < 300 and room_list[index+1].Room_visited > room.Room_visited): # Huske at vurdere der ikke er gået for lang tid siden man gik i midterste rum 
            break
        
        elif(room_list[index-room_list_len].Room_visited != 0):
          
          timing["time_in_bathroom"] = room_list[-2].Room_visited - timing["time_in_bathroom"]
          timing["time_to_bedroom"] = room_list[0].Room_visited - room_list[-2].Room_visited
          self.MYSQL_Server.store_bathroom_event(timing)
    else:
      if(room_list[0].Room_visited < room_list[-1].Room_visited and room_list[0].Room_visited != 0):
       
        timing["start_time"] = room_list[0].Room_visited
        timing["time_to_bathroom"] = room_list[-1].Room_visited - room_list[0].Room_visited
        timing["time_in_bathroom"] = room_list[-1].Room_visited
        room_list[0].Room_visited = 0
      for index, room in enumerate(room_list):
        if(index != room_list_len):
          #if(room_list[-1].Room_visited != 0 and room_list[index])
          if(room_list[-1].Room_visited != 0 and room_list[-2-index].Room_visited - room_list[-1-index].Room_visited < 300 and room_list[-1-index].Room_visited > room.Room_visited):
            break
        
        
    #for room in room_list:
    #  print(room.Room_visited)
    #if(all(times != 0 for times in timing.values())):
      


    #start tid = Tid_sensor1
    #længde tid bad = Tid_sensor5-Tid_sensor1
    #tid på badeværelse =  Tid_sensor4_anden_gang - Tid_sensor5_første_gang
    #længde tid soveværelse Tid_sensor1_anden_gang - Tid_sensor4




  def sanitize_message(self, client, userdata, message) -> dict:
    for sensor in sensor_list:
      if f"{sensor}" in message.topic:  
        payload_recieve = message.payload.decode("utf-8")
        payload_recieve = json.loads(payload_recieve)
        payload_recieve.update ({"SENSOR_ID": sensor.partition("R")[2]})
        room_num_index = int(payload_recieve["SENSOR_ID"]) - 1 
        if (payload_recieve["occupancy"] == "true"):
          #self.set_room_visited(self, room_list, room_num_index)
          #client.publish(topic=f"zigbee2mqtt/LED{payload_recieve["SENSOR_ID"]}/set", payload=json.dumps({"state": "ON"}))
          client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"state": "OFF"}))
          self.MYSQL_Server.store_sensor_event(room_num_index+1)
          self.room_list[room_num_index].Room_visited = int(time.time())

          self.bathroom_event(self.room_list, timing)
        elif (self.room_list[room_num_index].Room_visited != 0 and  int(time.time()) - self.room_list[room_num_index].Room_visited > 5):
          client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"state": "ON"}))
          self.room_list[room_num_index].Room_visited  = 0 ### måske ændres

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
    #mqtt_client.subscribe("zigbee2mqtt/SENSOR1")
    
    # Start the subscriber thread.
    sleep(3)
    #mqtt_client.publish(topic="zigbee2mqtt/SENSOR1", payload=json.dumps({"occupancy": "true"}))
    
    x = 1
    
    try:
      mqtt_client.publish(topic="zigbee2mqtt/SENSOR1", payload=json.dumps({"occupancy": "true"}))
      sleep(3)
      mqtt_client.publish(topic="zigbee2mqtt/SENSOR2", payload=json.dumps({"occupancy": "true"}))
      sleep(3)
      mqtt_client.publish(topic="zigbee2mqtt/SENSOR3", payload=json.dumps({"occupancy": "true"}))
      sleep(3)
      mqtt_client.publish(topic="zigbee2mqtt/SENSOR4", payload=json.dumps({"occupancy": "true"}))
      sleep(3)
      mqtt_client.publish(topic="zigbee2mqtt/SENSOR5", payload=json.dumps({"occupancy": "true"}))
      sleep(3)
      mqtt_client.publish(topic="zigbee2mqtt/SENSOR5", payload=json.dumps({"occupancy": "true"}))
      sleep(3)
      mqtt_client.publish(topic="zigbee2mqtt/SENSOR4", payload=json.dumps({"occupancy": "true"}))
      sleep(3)
      mqtt_client.publish(topic="zigbee2mqtt/SENSOR3", payload=json.dumps({"occupancy": "true"}))
      sleep(3)
      mqtt_client.publish(topic="zigbee2mqtt/SENSOR2", payload=json.dumps({"occupancy": "true"}))
      sleep(3)
      mqtt_client.publish(topic="zigbee2mqtt/SENSOR1", payload=json.dumps({"occupancy": "true"})) 
      
      sleep(3)
      print("DONE WITH SENDING MESSAGES")   
      while True:
        print(f"Waiting ...{x}")
        sleep(2)
    except KeyboardInterrupt:
      print("Oh! you pressed CTRL + C.")
      print("Program interrupted.")
    finally:
      self.MYSQL_Server.mysql_conn.close()
      print("Closed MySQL connection!")







