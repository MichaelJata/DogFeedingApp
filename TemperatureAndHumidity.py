
"""This module provides possibilities to upload sensor data
from a DHT22 sensor to the IP Symcon home automation system"""
from time import sleep
from Symcon import Symcon
import pigpio
import DHT22

class TemperatureAndHumidity:
    """Class for managing the measurement of temperature and humidity"""
    SLEEP_TIME = 1

    def __init__(self):
        self.humidity = None
        self.temperature = None
        # Initiate GPIO for pigpio
        self.pi = pigpio.pi()
        
        # setup the sensor
        self.sensor = DHT22.sensor(self.pi, 25)  # BCM (description) reference, Board (Pin Numbers)
        self.sensor.trigger() # ???

    def read_data_from_sensor(self):
        """Reads from the DHT22 sensor and returns TEMPERATURE and HUMIDITY"""

        self.sensor.trigger()
        self.humidity = round(self.sensor.humidity(), 2)
        self.temperature = round(self.sensor.temperature(), 2)

    def start_sending_sensor_data_to_symcon(self):
        """Starts sending data to Symcon every 3 seconds"""

        while True:
            symcon = Symcon()
            self.read_data_from_sensor()
            print(f'Humidity is {self.humidity} % ')
            symcon.invoke_ips_rpc(method='SetValue', parameters=[45731, self.humidity])
            print(f"Temperature is: {self.temperature}  C")
            symcon.invoke_ips_rpc(method='SetValue', parameters=[25622, self.temperature])
            sleep(self.SLEEP_TIME)

# worker = TemperatureAndHumidity()
# worker.read_data_from_sensor()
# while worker.humidity <= 0:
#     print(worker.humidity)
#     worker.read_data_from_sensor()
#     print ("reading")
#     sleep(1)
# print(worker.temperature)
# print(worker.humidity)
#worker.start_sending_sensor_data_to_symcon()