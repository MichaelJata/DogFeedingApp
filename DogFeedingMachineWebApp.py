""" Main Flask Web App Module"""
import  math
# ,flash, redirect,  , session, abort
from flask import Flask, render_template, request
import json
import time
from DataAccess import DataAccess
import RPi.GPIO as GPIO
from DogFeeder import DogFeeder
from TemperatureAndHumidity import TemperatureAndHumidity

app = Flask(__name__)

@app.route("/")
def index():
    """This is the landing page"""
    page = request.args.get("page")
    if page is None:
        page = int(0)
    else:
        page = int(request.args.get("page"))

    items_per_page = int(5)
    data_access = DataAccess()
    feed_history_offset = items_per_page * (page - 1)
    feed_history = data_access.get_feed_history_with_columns(feed_history_offset, items_per_page)
    amount_of_feed_entries = data_access.get_amount_of_feed_entries()
    feed_limit = data_access.get_feed_limit()
    food_served_today = data_access.get_total_food_served_today()
    daily_feed_history = data_access.get_daily_feed_history()
    pages = math.ceil(amount_of_feed_entries[0] / items_per_page)
   
    climate_sensor = TemperatureAndHumidity()
    climate_sensor.read_data_from_sensor()
    while climate_sensor.humidity <= 0:
        print(climate_sensor.humidity)
        climate_sensor.read_data_from_sensor()
        print("reading")
        time.sleep(1)
    print(climate_sensor.temperature)
    print(climate_sensor.humidity)


    device_info = data_access.get_device_info()
    fill_status_progress_class = "bg-success"
    fill_level = int(device_info[1])
    if(fill_level < 30):
        fill_status_progress_class = "bg-danger"
    elif(fill_level < 60):
        fill_status_progress_class = "bg-warning"
            
    return render_template("dashboard.html", **locals())


@app.route('/feed', methods = ['POST', 'GET'])
def feed():
    """Accepts posted amount of food and starts feeding process"""
    if request.method == 'POST':
        page = request.args.get("page")
    if page is None:
        page = int(0)
    else:
        page = int(request.args.get("page"))
    
    items_per_page = int(5)
    feed_history_offset = items_per_page * (page - 1)
    feeder_name_input = request.form['feederNameInput']
    amount_of_food_input = int(request.form['amountOfFoodInput'])
    data_access = DataAccess()
    feed_history = data_access.get_feed_history_with_columns(feed_history_offset, items_per_page)
    amount_of_feed_entries = data_access.get_amount_of_feed_entries()
    feed_limit = data_access.get_feed_limit()
    food_served_today = data_access.get_total_food_served_today()
    daily_feed_history = data_access.get_daily_feed_history()

    add_food_result = data_access.add_feed_history(amount_of_food_input, feeder_name_input)
    if add_food_result == "success":
        operation_status_result = data_access.set_operation_status(1)
        """try:
            dog_feeder = DogFeeder()
            dog_feeder.feed_dog(amount_of_food_input)
            GPIO.cleanup()
            dog_feeder.initialize_status_led()
            dog_feeder.change_led_color_for_fill_level()
        except:
            GPIO.cleanup()"""
        time.sleep(10)
        operation_status_result = data_access.set_operation_status(0)

    pages = math.ceil(amount_of_feed_entries[0] / items_per_page)

    device_info = data_access.get_device_info()
    fill_status_progress_class = "bg-success"
    fill_level = int(device_info[1])
    if(fill_level < 30):
        fill_status_progress_class = "bg-danger"
    elif(fill_level < 60):
        fill_status_progress_class = "bg-warning"

    return render_template("dashboard.html", **locals())


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=5666)
