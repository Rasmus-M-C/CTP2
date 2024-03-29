from time import sleep
from Misc.Cep2Controller import Cep2Controller
from Cep2Model import Cep2Model, Cep2ZigbeeDevice


if __name__ == "__main__":
    # Create a data model and add a list of known Zigbee devices.
    devices_model = Cep2Model()
    devices_model.add([Cep2ZigbeeDevice("0x00158d00044c228a", "pir"),
                       Cep2ZigbeeDevice("0xccccccfffeeaa775", "led"),
                       Cep2ZigbeeDevice("0xddddddfffeeaa775", "power plug")])

    # Create a controller and give it the data model that was instantiated.
    controller = Cep2Controller(devices_model)
    controller.start()

    print("Waiting for events...")

    while True:
        sleep(1)

    controller.stop()
