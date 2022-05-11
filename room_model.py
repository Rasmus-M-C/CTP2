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

  def set_room_visited(self, Room_visisted):
    self.Room_visisted = True

    #self.occupied_thread.start()
  def sanitize_message(self, client, userdata, message) -> dict:
    for sensor in sensor_list:
      if f"{sensor}" in message.topic:  
        payload_recieve = message.payload.decode("utf-8")
        payload_recieve = json.loads(payload_recieve)
        payload_recieve.update ({"SENSOR_ID": sensor.partition("R")[2]})
        room_num_index = payload_recieve = int(["SENSOR_ID"]) - 1 
        if (room_list[room_num_index].Internal_counter % 5 == 0):
          if (payload_recieve["occupancy"] == True):

            client.publish(topic=f"zigbee2mqtt/LED{payload_recieve[SENSOR_ID]}", payload=json.dumps({"state": "OFF"}))

        else: 
            client.publish(topic=f"zigbee2mqtt/NY_LED_WORKS_YES/set", payload=json.dumps({"state": "OFF"}))
        #if(payload_recieve["occupancy"]==True):
  def is_room_visited(self, payload_recieve) -> None:
    if (payload_recieve["occupancy"]==True):
      self.room_id.Room_visited = True

  def control_loop(self):
    # Create a data model and add a list of known Zigbee devices.
    mqtt_client= MqttClient()
    # Connect to the host given in initializer.
    mqtt_client.connect(self.room_id.Host, self.room_id.Port)
    mqtt_client.on_message = self.sanitize_message
    mqtt_client.loop_start()
    # Subscribe to all topics given in the initializer.
    #mqtt_client.subscribe("zigbee2mqtt/#")
    #print(self.room_id.Room_visited)
    mqtt_client.subscribe("zigbee2mqtt/#")
    mqtt_client.subscribe("zigbee2mqtt/{self.room_id.id_sensor}")
    
    # Start the subscriber thread.
   

    while True:
        sleep(1)







