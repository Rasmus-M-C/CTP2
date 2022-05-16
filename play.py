import time
import threading
from dataclasses import dataclass
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
  

room1 = Room("SENSOR1","LED1","127.0.0.1", 1883)
room_list = [room1]  
my_list = ["1","2","3", "4", "5"]
timing = {"start_time": 2, "time_to_bathroom": 0, "time_in_bathroom": 0, "time_to_bedroom": 0}
def is_time_correct() -> bool:
   operating_time = [22 , 23 , 24 , 00 , 1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 , 15]
   t = time.localtime()
   current_time = int(time.strftime("%H", t))
   return(current_time not in operating_time)
print(all(room_list))

#f, item in my_list[::-1]:
   # print (item)
