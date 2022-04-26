import json
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish, subscribe
from time import sleep, time
import classes, threading
HOST = "127.0.0.1"
PORT = 1883

def is_time_correct():
    t = time.localtime()
    current_time = time.strftime("%H", t)
    timenow = int(current_time)
    if (timenow == 22 or 23 or 24 or 00 or 1 or 2 or 3 or 4 or 5 or 6 or 7 or 8):
        return True
    else:
        return False

 # def change_state(self, device_id: str, state: str) -> None:
 #   if not self.__connected:
 #       raise RuntimeError("The client is not connected. Connect first.")
 #
 #   self.__client.publish(topic=f"zigbee2mqtt/{device_id}/set",
 #                           payload=json.dumps({"state": f"{state}"}))

def process_sensor(client, message):
    print("msg received")
    if "SENSOR1" in message.topic:
        payload_recieve = message.payload.decode("utf-8")
        payload_recieve = json.loads(payload_recieve)
        print(payload_recieve)
        if(payload_recieve["occupancy"]==True):
          client.publish(topic=f"zigbee2mqtt/NY_LED_WORKS_YES/set", payload=json.dumps({"state": "ON"}))
          threading.Timer(30, process_sensor(client, message)).start()
        else: 
          client.publish(topic=f"zigbee2mqtt/NY_LED_WORKS_YES/set", payload=json.dumps({"state": "OFF"}))

if __name__ == "__main__":
    # Create a data model and add a list of known Zigbee devices.
    mqtt_client= MqttClient()
  
    # Connect to the host given in initializer.
    mqtt_client.connect(HOST, PORT)
    mqtt_client.on_message = process_sensor
    mqtt_client.loop_start()
    # Subscribe to all topics given in the initializer.
    mqtt_client.subscribe("zigbee2mqtt/#")
    mqtt_client.subscribe("zigbee2mqtt/NY_LED_WORKS_YES")
   
    # Start the subscriber thread.
   

    while True:
        sleep(1)
