import json
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish, subscribe
from time import sleep
HOST = "127.0.0.1"
PORT = 1883

def __on_message(self, client, userdata, message) -> None:
    payload = message.payload.decode("utf-8")
    payload_recieve = json.loads(payload_recieve)
    if(payload_recieve.topic=="0x00158d00057b4d2a"):
        if(payload_recieve.occupancy==True):
            self.publish(topic=f"zigbee2mqtt/0x60a423fffe023458/set",
                    payload_send=json.dumps({"effect": "blink"}))

if __name__ == "__main__":
    # Create a data model and add a list of known Zigbee devices.
    mqtt_client= MqttClient()
  
    # Connect to the host given in initializer.
    mqtt_client.on_connect=__on_connect
    mqtt_client.on_subscribe = __on_subscribe
    mqtt_client.connect(HOST, PORT)
    mqtt_client.on_message = __on_message
    mqtt_client.loop_start()
    # Subscribe to all topics given in the initializer.
    mqtt_client.subscribe("zigbee2mqtt/0x00158d00057b4d2a")
    mqtt_client.subscribe("zigbee2mqtt/0x60a423fffe023458")
   
    # Start the subscriber thread.
   

    while True:
        sleep(1)
