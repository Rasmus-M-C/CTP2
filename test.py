import json
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish, subscribe
from time import sleep, time
import threading
import room_model
import main
HOST = "127.0.0.1"
PORT = 1883

mqtt_client = MqttClient()
mqtt_client.connect("127.0.0.1", 1883)

def send_message_sensor(sensor_id: int, mqtt_client, value: bool, sleep_time: int):
    if(value):mqtt_client.publish(topic=f"zigbee2mqtt/SENSOR{sensor_id}", payload=json.dumps({"occupancy": True}))
    else: mqtt_client.publish(topic=f"zigbee2mqtt/SENSOR{sensor_id}", payload=json.dumps({"occupancy": False}))
    sleep(sleep_time)
if __name__ == "__main__":
    mqtt_client = MqttClient()
    mqtt_client.connect("127.0.0.1", 1883)
    send_message_sensor(1, mqtt_client, True, 1)
    send_message_sensor(2, mqtt_client, True, 1)
    send_message_sensor(3, mqtt_client, True, 3)
    send_message_sensor(2, mqtt_client, True, 1) 
    send_message_sensor(1, mqtt_client, True, 1)     
    send_message_sensor(3, mqtt_client, True, 1)
    #send_message_sensor(4, mqtt_client, True, 1)
    #send_message_sensor(5, mqtt_client, True, 1)
    #send_message_sensor(5, mqtt_client, True, 1)
    #send_message_sensor(4, mqtt_client, True, 1)
    #send_message_sensor(3, mqtt_client, True, 1)
    #send_message_sensor(2, mqtt_client, True, 1)
    #send_message_sensor(1, mqtt_client, True, 1)