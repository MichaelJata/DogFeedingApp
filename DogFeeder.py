import RPi.GPIO as GPIO
import time
from Scale.ScaleLogic import ScaleLogic

class DogFeeder:
    """This class is responsible for the sensor and actor interaction for the dog feeder machine """
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.DCMOTOR_FORWARD_PIN    = 2
        self.DCMOTOR_BACKWARD_PIN   = 3
        self.LOADCELL_DATAOUT       = 6
        self.LOADCELL_PDSCK         = 5
        self.STEPPERMOTOR_COILA1PIN = 4
        self.STEPPERMOTOR_COILA2PIN = 17
        self.STEPPERMOTOR_COILB1PIN = 27
        self.STEPPERMOTOR_COILB2PIN = 22

        self.debug_mode = False
        self.weight_sensor = ScaleLogic(self.LOADCELL_DATAOUT,self.LOADCELL_PDSCK)

        """The sensor has not enough space in casing, 
        hence the 15% angle it requires to both sides is not given. 
        If the box is almost empty, every second value is over 3000cm. 
        These values will be filtered out"""
        self.FALSE_PEAK_VALUE = 3000 
        self.STEPS_BETWEEN_START_END = int(2150)
        self.DELAY_BETWEEN_STEPS = 0.001 #seconds

        self.current_led_color = None


        GPIO.setup(self.DCMOTOR_FORWARD_PIN, GPIO.OUT)
        GPIO.setup(self.DCMOTOR_BACKWARD_PIN, GPIO.OUT)
        GPIO.setup(self.STEPPERMOTOR_COILA1PIN, GPIO.OUT)
        GPIO.setup(self.STEPPERMOTOR_COILA2PIN, GPIO.OUT)
        GPIO.setup(self.STEPPERMOTOR_COILB1PIN, GPIO.OUT)
        GPIO.setup(self.STEPPERMOTOR_COILB2PIN, GPIO.OUT)
        
        #make sure the DC motor is off when pins are initialized
        GPIO.output(self.DCMOTOR_FORWARD_PIN, GPIO.LOW)
        GPIO.output(self.DCMOTOR_BACKWARD_PIN, GPIO.LOW)

        self.initialize_status_led()
    
    def initialize_status_led(self):
        if GPIO.getmode() != 11:
            GPIO.setmode(GPIO.BCM)

        self.RGBLED_BLUE_PIN        = 18
        self.RGBLED_GREEN_PIN       = 15
        self.RGBLED_RED_PIN         = 14
        self.ULTRASONIC_TRIGGER_PIN = 23
        self.ULTRASONIC_ECHO_PIN    = 24
        GPIO.setup(self.RGBLED_BLUE_PIN, GPIO.OUT)
        GPIO.setup(self.RGBLED_GREEN_PIN, GPIO.OUT)
        GPIO.setup(self.RGBLED_RED_PIN, GPIO.OUT)
        GPIO.setup(self.ULTRASONIC_TRIGGER_PIN, GPIO.OUT)
        GPIO.setup(self.ULTRASONIC_ECHO_PIN, GPIO.IN)

    def turn_on_light_green(self):
        """Turns the RGB LED on in green color"""
        GPIO.output(self.RGBLED_BLUE_PIN, 0)
        GPIO.output(self.RGBLED_GREEN_PIN, 1)
        GPIO.output(self.RGBLED_RED_PIN, 0)
        self.current_led_color = "green"

    def turn_on_light_yellow(self):
        """Turns the RGB LED on in yellow color"""
        GPIO.output(self.RGBLED_BLUE_PIN, 0)
        GPIO.output(self.RGBLED_GREEN_PIN, 1)
        GPIO.output(self.RGBLED_RED_PIN, 1)
        self.current_led_color = "yellow"

    def turn_on_light_red(self):
        """Turns the RGB LED on in red color"""
        GPIO.output(self.RGBLED_BLUE_PIN, 0)
        GPIO.output(self.RGBLED_GREEN_PIN, 0)
        GPIO.output(self.RGBLED_RED_PIN, 1)
        self.current_led_color = "red"

    def __get_distance_to_food(self):
        """Returns the distance to the food indicating the fill level"""
        GPIO.output(self.ULTRASONIC_TRIGGER_PIN, True)
        time.sleep(0.00001)
        GPIO.output(self.ULTRASONIC_TRIGGER_PIN, False)
 
        start_time = time.time()
        stop_time = time.time()
 
        while GPIO.input(self.ULTRASONIC_ECHO_PIN) == 0:
            start_time = time.time()
 
        while GPIO.input(self.ULTRASONIC_ECHO_PIN) == 1:
            stop_time = time.time()
 
        time_elapsed = stop_time - start_time
        # divided by velocity of sound and 2 as we want a single way
        distance = (time_elapsed * 34300) / 2
        if distance < self.FALSE_PEAK_VALUE:
            return distance

    def change_led_color_for_fill_level(self):
        """Changes the LED color to indicate the food fill state"""
        distance_to_food = None
        while distance_to_food is None:
            distance_to_food = self.__get_distance_to_food()
            time.sleep(1)

        print(distance_to_food)

        
        if distance_to_food >= 30:
            self.turn_on_light_red()
        elif distance_to_food >= 10:
            self.turn_on_light_yellow()
        else:
            self.turn_on_light_green()

    def move_dcmotor_forward_autostop(self,x):
        """Moves the DC motor clockwise, thus the spiral conveyor moves the food down for a specified time"""
        self.move_dcmotor_forward()
        time.sleep(x)
        GPIO.output(self.DCMOTOR_FORWARD_PIN, GPIO.LOW)

    def move_dcmotor_backward_autostop(self,x):
        """Moves the DC motor counter clockwise, thus the spiral conveyor moves the food up for a specified time"""
        self.move_dcmotor_backward()
        time.sleep(x)
        GPIO.output(self.DCMOTOR_BACKWARD_PIN, GPIO.LOW)

    def move_dcmotor_forward(self):
        """Moves the DC motor clockwise, thus the spiral conveyor moves the food down"""
        GPIO.output(self.DCMOTOR_FORWARD_PIN, GPIO.HIGH)
        if self.debug_mode:
            print("Moving Forward")

    def move_dcmotor_backward(self):
        """Moves the DC motor counter clockwise, thus the spiral conveyor moves the food up"""
        GPIO.output(self.DCMOTOR_BACKWARD_PIN, GPIO.HIGH)
        print("Moving Backward")

    def stop_dcmotor_forward_movement(self):
        """Stops the DC motor after moving forward"""
        GPIO.output(self.DCMOTOR_FORWARD_PIN, GPIO.LOW)

    def stop_dcmotor_backward_movement(self):
        """Stops the DC motor after moving backwards"""
        GPIO.output(self.DCMOTOR_BACKWARD_PIN, GPIO.LOW)

    def __set_steppermotor_step(self,w1, w2, w3, w4):
        """By setting the steps in a specific order, the stepper motor starts 'spinning'"""
        GPIO.output(self.STEPPERMOTOR_COILA1PIN, w1)
        GPIO.output(self.STEPPERMOTOR_COILA2PIN, w2)
        GPIO.output(self.STEPPERMOTOR_COILB1PIN, w3)
        GPIO.output(self.STEPPERMOTOR_COILB2PIN, w4)

    def move_steppermotor_forward(self, delay, steps):
        """Makes the stepper motor move clockwise, thus making the sliding carriage move right to the start position """
        for i in range(0, steps):
            self.__set_steppermotor_step(1, 0, 1, 0)
            time.sleep(delay)
            self.__set_steppermotor_step(0, 1, 1, 0)
            time.sleep(delay)
            self.__set_steppermotor_step(0, 1, 0, 1)
            time.sleep(delay)
            self.__set_steppermotor_step(1, 0, 0, 1)
            time.sleep(delay)
 
    def move_steppermotor_backward(self, delay, steps):
        """Makes the stepper motor move counter clockwise, thus making the sliding carriage move left to the direction where the hatch is positioned"""
        for i in range(0, steps):
            self.__set_steppermotor_step(1, 0, 0, 1)
            time.sleep(delay)
            self.__set_steppermotor_step(0, 1, 0, 1)
            time.sleep(delay)
            self.__set_steppermotor_step(0, 1, 1, 0)
            time.sleep(delay)
            self.__set_steppermotor_step(1, 0, 1, 0)
            time.sleep(delay)

    def move_steppermotor_to_start_position(self):
        """Moves the sliding carriage to start position"""
        self.move_steppermotor_forward(self.DELAY_BETWEEN_STEPS, self.STEPS_BETWEEN_START_END)

    def move_steppermotor_to_end_position(self):
        """Moves the sliding carriage to end position, i.e. the hatch location"""
        self.move_steppermotor_backward(self.DELAY_BETWEEN_STEPS, self.STEPS_BETWEEN_START_END)

    def get_weight_until(self, threshold):
        """Measures the weight until the weight is as much as the threshold"""
        self.weight_sensor.setReferenceUnit(-1842.1013)
        self.weight_sensor.reset()
        self.weight_sensor.tare()

        if self.debug_mode:
           print("Starting weighing food...")
        current_weight = 0
        while current_weight < threshold:
            current_weight = self.weight_sensor.getMeasure()
            if self.debug_mode:
                print(f"current weight is {current_weight}")

        if self.debug_mode:
            print(f"Threshold of {threshold} has been reached. It is {current_weight}")

    def feed_dog(self, food_in_grams):
        """Drops the specified amount of food (grams) to the dog's bowl"""
        self.move_dcmotor_forward()
        self.get_weight_until(food_in_grams)
        self.stop_dcmotor_forward_movement()
        self.move_steppermotor_to_end_position()
        self.move_steppermotor_to_start_position()



try:
    dog_feeder = DogFeeder()
    dog_feeder.feed_dog(370)
    GPIO.cleanup()
    dog_feeder.initialize_status_led()
    dog_feeder.change_led_color_for_fill_level()


except KeyboardInterrupt:
    GPIO.cleanup()