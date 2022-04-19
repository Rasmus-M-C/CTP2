from dataclasses import dataclass
import json
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish, subscribe
from time import sleep, time
import threading

from AU_programmering.Projekt.CTP2.test import process_sensor

@dataclass
class Room:

  id_sensor: str
  id_LED: str
  previous_room_visited: bool
  next_room_visited: bool
  Host: str
  Port: int

  def process_sensor(self, client, message) -> None:
    if self.id_sensor in message.topic:
      payload_recieve = message.payload.decode("utf-8")
      payload_recieve = json.loads(payload_recieve)
      print(payload_recieve)
      if(payload_recieve["occupancy"]==True):
          client.publish(topic=f"zigbee2mqtt/{self.id_LED}/set", payload=json.dumps({"state": "ON"}))
          threading.Timer(30, process_sensor(self, client, message)).start()
      else: 
          client.publish(topic=f"zigbee2mqtt/{self.id_LED}/set", payload=json.dumps({"state": "OFF"}))




