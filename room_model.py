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
Can_log = False
Old_time = 0
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

  def __init__(self,id_sensor, id_LED, Host, Port):
    self.Id_sensor = id_sensor
    self.Id_LED = id_LED
    self.Host = Host
    self.Port = Port
  
  #Methods 

@dataclass
class Server(): # Database classm, which attributes for using MySQL
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

  def store_sensor_event(self, room_id: int): # Logs a sensor event aka sensor activation
    
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S') # Current time in SQL format
    
    cursor = self.mysql_conn.cursor()
    insert_stmt = ("INSERT INTO sensordata (room_id, device_type, measurement, timestamp)"
     "VALUES (%s, %s, %s, %s)") ## Table values
    data = (str(room_id),str('PIR Sensor'), str(True), formatted_date)
    cursor.execute(insert_stmt, data)
    self.mysql_conn.commit()
    print(f"Logged sensor data from {room_id}")
    #self.mysql_conn.close()
  
  def store_bathroom_event(self, timing: dict, room_list: list): # Logs a bathroom event

    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S') # Current time in SQL format
    
    cursor = self.mysql_conn.cursor()
    insert_stmt = ("INSERT INTO bathroom_data (time_to_bathroom, time_in_bathroom, time_to_bedroom, timestamp)"
     "VALUES (%s, %s, %s, %s)") ## Table values
    data = (timing["time_to_bathroom"], timing["time_in_bathroom"], timing["time_to_bedroom"], formatted_date)
    cursor.execute(insert_stmt, data)
    self.mysql_conn.commit()
    for room in room_list:
      room.Room_visited = 0
    timing["start_time"] = 0
    timing["time_to_bathroom"] = 0 
    timing["time_in_bathroom"] = 0 
    timing["time_to_bedroom"] = 0
    print("Logged bathroom event")
    #self.mysql_conn.close()



@dataclass
class Controller(): # changes model aka rooms
  room_list: list
  MYSQL_Server: Server
  def __init__(self, room_list_input, input_server):
    self.room_list = room_list_input
    self.MYSQL_Server = input_server
  
  
  def bathroom_event(self, room_list: list, timing: dict, vv: bool): # Checks if conditions for bathroom visit are fulfilled
    
    room_list_len = len(room_list)-1
    # Below, checks if every sensor has a time of activation such that the person is actually moving towards the bathroom
    #¤timing["start_time"] = room_list[0].Room_visited
    if((timing["start_time"] == 0) or (int(time.time()) - timing["start_time"] > 30)): 
      timing["start_time"] = room_list[0].Room_visited
      vv = True
    #if(int(time.time()) - room_list[0].Room_visited  > int(time.time()) - room_list[-1].Room_visited):
     # vi kommer fra soveværelset
    if((timing["time_in_bathroom"] == 0) or (int(time.time()) - timing["start_time"] > 30 ) or (vv) ): 
      timing["time_in_bathroom"] = room_list[-1].Room_visited
      #Old_time = room_list[-1].Room_visited
      vv = False

    
    if(((room_list[-1].Room_visited != 0)and(timing["time_to_bathroom"] == 0))): 
      timing["time_to_bathroom"] = room_list[-1].Room_visited - timing["start_time"]
    for index, room in enumerate(room_list):
      if(index != room_list_len):
        if((room_list[index].Room_visited != 0) and ((room_list[-1].Room_visited - timing["start_time"]) < (15*(room_list_len+1) )) and (all(room.Room_visited != 0 for room in room_list))): # Huske at vurdere der ikke er gået for lang tid siden man gik i midterste rum 
          if(room_list[0].Room_visited > timing["start_time"]): 
            #If the person has gone to the bathroom and back to the bedroom, we can log a bathroom event
            
            timing["time_in_bathroom"] = room_list[-2].Room_visited - timing["time_in_bathroom"]
            timing["time_to_bedroom"] = room_list[0].Room_visited - room_list[-2].Room_visited
            self.MYSQL_Server.store_bathroom_event(timing, room_list)
      #print(room_list[0].Room_visited)
      #print(timing["start_time"])
      #timing["time_to_bathroom"] = room_list[-1].Room_visited - timing["start_time"]
      #elif(room_list[0].Room_visited > timing["start_time"]): 
      #  #If the person has gone to the bathroom and back to the bedroom, we can log a bathroom event
      #  timing["time_in_bathroom"] = room_list[-2].Room_visited - timing["time_in_bathroom"]
      #  timing["time_to_bedroom"] = room_list[0].Room_visited - room_list[-2].Room_visited
      #  self.MYSQL_Server.store_bathroom_event(timing, room_list)
    # Below checks if the person has moved back to the bedroom
    #else:
    #  if(room_list[0].Room_visited < room_list[-1].Room_visited):
    #   
    #    
    #    
    #  for index, room in enumerate(room_list):
    #    if(index != room_list_len):
    #      #if(room_list[-1].Room_visited != 0 and room_list[index])
    #      if(room_list[-1].Room_visited != 0 and room_list[-2-index].Room_visited - room_list[-1-index].Room_visited < 50 and room_list[-1-index].Room_visited > room.Room_visited):
    #        break
        
    #start tid = Tid_sensor1
    #længde tid bad = Tid_sensor5-Tid_sensor1
    #tid på badeværelse =  Tid_sensor4_anden_gang - Tid_sensor5_første_gang
    #længde tid soveværelse Tid_sensor1_anden_gang - Tid_sensor4
  def color_room(self, sensor_id: int, client):
    
    if(sensor_id == 1):
      client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"state": "ON"}))
      client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"color": {"hex":"#FF0000"}})) #Rød
    elif(sensor_id == 2):
      client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"state": "ON"}))
      client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"color": {"hex":"#00FF00"}})) #Grøn
    elif(sensor_id == 3):
      client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"state": "ON"}))
      client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"color": {"hex":"#0000FF"}})) #Blå
    elif(sensor_id == 4):
      client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"state": "ON"}))
      client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"color": {"hex":"#FFFF00"}})) #Gul
    elif(sensor_id == 5):
      client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"state": "ON"}))
      client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"color": {"hex":"#FFB7D1"}})) #Pink

  def send_message_sensor(self, sensor_id: int, mqtt_client):
    mqtt_client.publish(topic=f"zigbee2mqtt/SENSOR{sensor_id}", payload=json.dumps({"occupancy": "true"}))
    sleep(1)

  
  #def sanitize_and_turn_on_room_and_next_room(self, client, userdata, message) -> dict:
  #  for sensor in sensor_list:
  #    if f"{sensor}" in message.topic:  
  #      payload_recieve = message.payload.decode("utf-8")
  #      payload_recieve = json.loads(payload_recieve)
  #      payload_recieve.update ({"SENSOR_ID": sensor.partition("R")[2]})
  #      room_num_index = int(payload_recieve["SENSOR_ID"]) - 1 
  #      if (payload_recieve["occupancy"] == "true"):
  #        client.publish(topic=f"zigbee2mqtt/LED{room_num_index}/set", payload=json.dumps({"state": "ON"}))
  #        if(room_num_index != len(sensor_list)-1):
  #          client.publish(topic=f"zigbee2mqtt/LED{room_num_index+1}/set", payload=json.dumps({"state": "ON"}))
  #        if(room_num_index != 0):
  #          client.publish(topic=f"zigbee2mqtt/LED{room_num_index-1}/set", payload=json.dumps({"state": "ON"}))
  #        self.MYSQL_Server.store_sensor_event(room_num_index+1) # Store in database that sensor was activated
#
  #        self.room_list[room_num_index].Room_visited = int(time.time()) # Time of visit
  #        
  #        self.bathroom_event(self.room_list, timing) # Checks if conditions to bathroom trip is fulfilled
  #      
  #      elif (int(time.time()) - self.room_list[room_num_index].Room_visited > 30): # If 30 second has passed since we turned on the sensor
  #        client.publish(topic=f"zigbee2mqtt/LED{room_num_index}/set", payload=json.dumps({"state": "ON"})) # turn off the LED corresponding to sensor ID  
  #        self.room_list[room_num_index].Room_visited  = 0 # Set time of activation to 0, for bathroom_event to work correctly in its logic.
  #                                                         # The time is set to 0 after we turn the LED off because the person it out of view
  #
  #def is_old(self, room_list: list):
  #  for index in range(len(room_list)):


  def sanitize_message(self, client, userdata, message) -> dict:
    for sensor in sensor_list:
      if f"{sensor}" in message.topic:  
        payload_recieve = message.payload.decode("utf-8")
        payload_recieve = json.loads(payload_recieve)
        payload_recieve.update ({"SENSOR_ID": sensor.partition("R")[2]})
        room_num_index = int(payload_recieve["SENSOR_ID"]) - 1 
        if (payload_recieve["occupancy"] == True):
          #client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"color": {"hex":"#0000FF"}}))
          self.color_room(room_num_index+1, client)
          #client.publish(topic=f"zigbee2mqtt/LED{room_num_index}/set", payload=json.dumps({"color": {"hex":"#800080"}}))
          
          self.MYSQL_Server.store_sensor_event(room_num_index+1) # Store in database that sensor was activated

          self.room_list[room_num_index].Room_visited = int(time.time()) # Time of visit in room with tripped sensor

          self.bathroom_event(self.room_list, timing, Can_log) # Checks if conditions to bathroom trip is fulfilled

        elif (int(time.time()) - self.room_list[room_num_index].Room_visited > 25):
          client.publish(topic=f"zigbee2mqtt/LED1/set", payload=json.dumps({"state": "OFF"}))
          self.room_list[room_num_index].Room_visited  = 0 ### måske ændres

  def is_time_correct(self) -> bool: # Function to check if we should run the system or not
    operating_time = [22 , 23 , 24 , 00 , 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8]
    t = time.localtime()
    current_time = int(time.strftime("%H", t))
    return(current_time not in operating_time)
    
  def control_loop(self): # Loop for recieveing and processing MQTT messages 
    mqtt_client = MqttClient()
    mqtt_client.connect("127.0.0.1", 1883)
    mqtt_client.loop_start()
    mqtt_client.subscribe("zigbee2mqtt/#")
    mqtt_client.on_message = self.sanitize_message
    while True:
      if (self.is_time_correct()): continue
# 

      #mqtt_client.publish(topic="zigbee2mqtt/SENSOR1", payload=json.dumps({"occupancy": "true"}))
      #try:
      #  self.send_message_sensor(1, mqtt_client)
      #  self.send_message_sensor(2, mqtt_client)
      #  self.send_message_sensor(3, mqtt_client)
      #  self.send_message_sensor(4, mqtt_client)
      #  self.send_message_sensor(5, mqtt_client)
      #  self.send_message_sensor(5, mqtt_client)
      #  self.send_message_sensor(4, mqtt_client)
      #  self.send_message_sensor(3, mqtt_client)
      #  self.send_message_sensor(2, mqtt_client)
      #  self.send_message_sensor(1, mqtt_client)

      #  print("DONE WITH SENDING MESSAGES")   
   







