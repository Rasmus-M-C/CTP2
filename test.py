import json
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish, subscribe
from time import sleep
HOST = "127.0.0.1"
PORT = 1883

def __on_message(client, userdata, message):
    print("msg received")
    if "SENSOR1" in message.topic:
        payload_recieve = message.payload.decode("utf-8")
        payload_recieve = json.loads(payload_recieve)
        print(payload_recieve)
        if(payload_recieve["occupancy"]==True):
            client.publish(topic=f"zigbee2mqtt/NY_LED_WORKS_YES/set", payload=json.dumps({"effect": "blink"}))

if __name__ == "__main__":
    # Create a data model and add a list of known Zigbee devices.
    mqtt_client= MqttClient()
  
    # Connect to the host given in initializer.
    mqtt_client.connect(HOST, PORT)
    mqtt_client.on_message = __on_message
    mqtt_client.loop_start()
    # Subscribe to all topics given in the initializer.
    mqtt_client.subscribe("zigbee2mqtt/#")
    mqtt_client.subscribe("zigbee2mqtt/NY_LED_WORKS_YES")
   
    # Start the subscriber thread.
   

    while True:
        sleep(1)
