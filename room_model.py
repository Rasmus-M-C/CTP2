from dataclasses import dataclass
import json
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish, subscribe
from time import sleep, time
import threading
import test

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
class Controller(): # changes model aka rooms
  room_list: list
  def __init__(self, room_list_input):
    self.room_list = room_list_input
    #self.occupied_thread = self.threading.Timer(30.0, self.is_occupied(client, userdata, message))

  def set_room_visited(self, Room, index: int):
    self.room_list = True

  def set_room_not_visited(self, room_list: list, index: int):
    self.room_list[index].Is = False

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







