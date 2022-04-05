from __future__ import annotations
import json
import signal
from dataclasses import dataclass
from datetime import datetime
from distutils.util import strtobool
from queue import Empty, Queue
from threading import Event, Thread
from typing import Any, Dict, List, Union
from mysql.connector import (connect as mysql_connect,
                             errorcode as mysql_errorcode,
                             Error as MySqlError)
from paho.mqtt.client import Client as MqttClient, MQTTMessage
from paho.mqtt import publish


@dataclass
class Cep2EvemanEvent:
    device_id: str
    device_type: str
    measurement: Any
    timestamp: datetime

    def to_json(self) -> str:
        """ Create a JSON representation of the event.

        Returns:
            str: a JSON string.
        """
        return json.dumps({
            "device_id": self.device_id,
            "device_type": self.device_type,
            "measurement": self.measurement,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    @classmethod
    def from_json(cls, event: Union[str, Dict[str, Any]]) -> Cep2EvemanEvent:
        """ Instantiate a Cep2Event from a JSON string.

        Args:
            event (Union[str, Dict[str, Any]]): the JSON object as a string or as a dict.

        Returns:
            Cep2Event: object instantiated fro mthe JSON object.

        Raises:
            KeyError: if one of the object attributes is not found.
        """
        json_obj = json.loads(event) if isinstance(event, str) else event

        return cls(device_id=json_obj["device_id"],
                   device_type=json_obj["device_type"],
                   measurement=json_obj["measurement"],
                   timestamp=datetime.strptime(json_obj["timestamp"], "%Y-%m-%d %H:%M:%S"))


class Cep2EvemanModel:
    # IMPORTANT: this is a very simplistic example of a database, so th eexmaple is easier to
    # understand. By no measn this is a right approach for this database.
    # The first limitation of this database is the lack of a device table, which makes the database
    # not conform with the 2nd normal form (2NF), i.e. there should be a devices table that has
    # multiple events.
    # The second limitation is the generalization of data contained in the measurement column.
    # Relational databases (at least MySQL and SQLite) don't have a generic type for columns, thus
    # this approach is a workaraound for a generic storage in a single column. A better approach
    # would be an event table that holds the common event data, such as timestamp, that then is
    # related with a device table and tables for specific events (for example, occupancy or power
    # plug events).
    TABLES = {
        "events": ("CREATE TABLE `events` ("
                   "  `id` int(11) NOT NULL AUTO_INCREMENT,"
                   "  `device_id` varchar(30) NOT NULL,"
                   "  `device_type` varchar(30) NOT NULL,"
                   "  `measurement` varchar(30) NOT NULL,"
                   "  `timestamp` timestamp NOT NULL,"
                   "  PRIMARY KEY (`id`)"
                   ") ENGINE=InnoDB")
    }

    def __init__(self, host, database: str, user: str, password: str) -> None:
        self.__database = database
        self.__host = host
        self.__mysql_connection = None
        self.__user = user
        self.__password = password

    def connect(self):
        """ Connect to database given in the initializer. The connection is left open and must be
        closed explicitly by the user using disconnect().
        """

        # If the connection is already open, then don't do anything.
        if self.__mysql_connection:
            return
        try:
            self.__mysql_connection = mysql_connect(host=self.__host,
                                                    user=self.__user,
                                                    password=self.__password)
            # Select the database given in the initalizer. If it fails, an exception is raised, that
            # can be used to create the database.
            self.__mysql_connection.cursor().execute(f"USE {self.__database}")
        except MySqlError as err:
            # If the database doesn't exist, then create it.
            if err.errno == mysql_errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist. Will be created.")
                self.__create_database()
                print(f"Database {self.__database} created successfully.")
                self.__mysql_connection.database = self.__database
            else:
                print(f"Database error = {err}")

    def disconnect(self):
        """ Disconnect from the database.
        """
        self.__mysql_connection.close()
        self.__mysql_connection = None

    def get_events(self) -> List[Cep2EvemanEvent]:
        """ Gets the full list of events.

        Raises:
            RuntimeError: a connection to the database was not established.

        Returns:
            List[Cep2Event]: list of events
        """

        # A connection to the database was not established. Then, stop.
        if not self.__mysql_connection:
            raise RuntimeError(f"Not connected to database {self.__database}.")

        query = "SELECT device_id, device_type, measurement, timestamp FROM events;"
        cursor = self.__mysql_connection.cursor()
        events = []

        # Execute the SELECT query.
        cursor.execute(query)

        # Parse all the results from the query. The measurements are stored in the database as
        # strings. When parsing them, convert to the correct type.
        #

        for (did, dt, m, ts) in cursor:
            if m.isdigit():
                measurement = int(m)
            elif m.lower() in ("true", "false"):
                measurement = bool(strtobool(m))
            else:
                measurement = m

            events.append(Cep2EvemanEvent(device_id=did,
                                    device_type=dt,
                                    measurement=measurement,
                                    timestamp=ts))

        return events

    def store(self, event: Cep2EvemanEvent) -> None:
        if not self.__mysql_connection:
            raise RuntimeError(f"Not connected to database {self.__database}.")

        query = (f"INSERT INTO events (device_id,device_type,measurement,timestamp)"
                 f"VALUES(%s, %s, %s, %s);")
        cursor = self.__mysql_connection.cursor()

        # If the value is a boolean, then convert it to a string in the format "true" or "false".
        # Other value types will be automatically converted to a string, once the query is executed.
        measurement = (str(event.measurement).lower()if isinstance(event.measurement, bool)
                       else event.measurement)

        cursor.execute(query,
                       (event.device_id, event.device_type, measurement, event.timestamp))
        self.__mysql_connection.commit()

        cursor.close()

    def __create_database(self):
        cursor = self.__mysql_connection.cursor()

        try:
            cursor.execute(f"CREATE DATABASE {self.__database} DEFAULT CHARACTER SET 'utf8'")
        except MySqlError as err:
            print(f"Failed creating database: {err}")
        else:
            cursor.execute(f"USE {self.__database}")

            for table_name in self.TABLES:
                table_description = self.TABLES[table_name]
                try:
                    print(f"Creating table {table_name}: ", end="")
                    cursor.execute(table_description)
                except MySqlError as err:
                    if err.errno == mysql_errorcode.ER_TABLE_EXISTS_ERROR:
                        print(f"Table {table_name} already exists.")
                    else:
                        print(err.msg)
                else:
                    print("OK")

        cursor.close()
        self.__mysql_connection.database = self.__database


class Cep2EvemanController:
    TOPIC = "cep2/#"

    def __init__(self, mqtt_host: str, model: Cep2EvemanModel, mqtt_port: int = 1883) -> None:
        self.__connected = False
        self.__events_queue = Queue()
        self.__model = model
        self.__mqtt_client = MqttClient()
        self.__mqtt_client.on_connect = self.__on_connect
        self.__mqtt_client.on_disconnect = self.__on_disconnect
        self.__mqtt_client.on_message = self.__on_message
        self.__mqtt_host = mqtt_host
        self.__mqtt_port = mqtt_port
        self.__subscriber_thread = Thread(target=self.__worker,
                                          daemon=True)
        self.__stop_worker = Event()

    def start_listening(self) -> None:
        """ Start listening for published events.
        """
        # Connect to the database
        self.__model.connect()

        # In the client is already connected then stop here.
        if self.__connected:
            return

        # Connect to the host given in initializer.
        self.__mqtt_client.connect(self.__mqtt_host,
                              self.__mqtt_port)
        self.__mqtt_client.loop_start()
        # Subscribe to all topics given in the initializer.
        self.__mqtt_client.subscribe(self.TOPIC)
        # Start the subscriber thread.
        self.__subscriber_thread.start()

    def stop_listening(self) -> None:
        """ Stop listening for published events.
        """
        self.__stop_worker.set()
        self.__mqtt_client.loop_stop()
        self.__mqtt_client.unsubscribe(self.TOPIC)
        self.__mqtt_client.disconnect()

        # Disconnect from the database
        self.__model.disconnect()

    def __on_connect(self, client, userdata, flags, rc) -> None:
        """ Callback invoked when a connection with the MQTT broker is established.

        Refer to paho-mqtt documentation for more information on this callback:
        https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#callbacks
        """

        # Set connected flag to true. This is later used if multiple calls to connect are made. This
        # way the user does not need to very if the client is connected.
        self.__connected = True
        print("MQTT client connected")

    def __on_disconnect(self, client, userdata, rc) -> None:
        """ Callback invoked when the client disconnects from the MQTT broker occurs.

        Refer to paho-mqtt documentation for more information on this callback:
        https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#callbacks
        """

        # Set connected flag to false. This is later used if multiple calls to connect are made.
        # This way the user does not need to very if the client is connected.
        self.__connected = False
        print("MQTT client disconnected")

    def __on_message(self, client, userdata, message: MQTTMessage) -> None:
        """ Callback invoked when a message has been received on a topic that the client subscribed.

        Refer to paho-mqtt documentation for more information on this callback:
        https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#callbacks
        """

        # Push a message to the queue. This will later be processed by the worker.
        self.__events_queue.put(message)

    def __worker(self) -> None:
        """ This method pulls zigbee2mqtt messages from the queue of received messages, pushed when
        a message is received, i.e. by the __on_message() callback. This method will be stopped when
        the instance of zigbee2mqttClient disconnects, i.e. disconnect() is called and sets the
        __stop_worker event.
        """
        while not self.__stop_worker.is_set():
            try:
                # Pull a message from the queue.
                message = self.__events_queue.get(timeout=1)
            except Empty:
                # This exception is raised when the queue pull times out. Ignore it and retry a new
                # pull.
                pass
            else:
                # If a message was successfully pulled from the queue, then process it.
                # NOTE: this else condition is part of the try and it is executed when the action
                # inside the try does not throws and exception.
                # The decode() transforms a byte array into a string, following the utf-8 encoding.
                if not message:
                    return

                if message.topic == "cep2/request/store_event":
                    try:
                        event = Cep2EvemanEvent.from_json(message.payload.decode("utf-8"))
                        print(f"Storing event {event}")
                        self.__model.store(event)
                    except KeyError:
                        print(f"Malformed JSON event: {message}")
                elif message.topic == "cep2/request/get_events":
                    # A get_events was received. thus retrieve the values from the database and
                    # publish them to the response topic.
                    events = [e.to_json() for e in self.__model.get_events()]

                    publish.single(hostname=self.__mqtt_host,
                                   port=self.__mqtt_port,
                                   topic="cep2/response/get_events",
                                   payload=json.dumps(events))


if __name__ == "__main__":
    stop_daemon = Event()

    def shutdown(signal, frame):
        stop_daemon.set()

    # Subscribe to signals sent from the terminal, so that the application is shutdown properly.
    # When one of the trapped signals is captured, the function shutdown() will be execute. This
    # will set the stop_daemon event that will then stop the loop that keeps the application running.
    signal.signal(signal.SIGHUP, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Instante model to connect to a database running in the same machine (localhost).
    model = Cep2EvemanModel(host="192.168.65.51",
                           database="Sensordata",
                           user="pi",
                           password="admin")
    # The controller will connect to a MQTT broker running in the same machine.
    controller = Cep2EvemanController(model=model,
                                     mqtt_host="localhost")

    controller.start_listening()

    while not stop_daemon.is_set():
        # The event times out evey 60 seconds, or when the event is set. If it is set, then the loop
        # will stop and the application will exit.
        stop_daemon.wait(60)

    controller.stop_listening()