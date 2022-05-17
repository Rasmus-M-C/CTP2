import json
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish, subscribe
from time import sleep, time
import threading
import room_model
HOST = "127.0.0.1"
PORT = 1883



if __name__ == "__main__":
    
    room1 = room_model.Room("SENSOR1","LED1","127.0.0.1", 1883)
    room2 = room_model.Room("SENSOR2","LED1","127.0.0.1", 1883)
    room3 = room_model.Room("SENSOR3","LED1","127.0.0.1", 1883)
    room4 = room_model.Room("SENSOR4","LED1","127.0.0.1", 1883)
    room5 = room_model.Room("SENSOR5","LED1","127.0.0.1", 1883)
    
    MYSQL_Server = room_model.Server(
    'dokkedalleth_dk', 
    'kodeord1234', 
    'mysql23.unoeuro.com', 
    'dokkedalleth_dk_db_events')
    
    room_list = []
    room_list.append(room1)
    room_list.append(room2)
    room_list.append(room3)
    room_list.append(room4)
    room_list.append(room5)
    controller1 = room_model.Controller(room_list, MYSQL_Server)
    
    controller1.control_loop()

#
