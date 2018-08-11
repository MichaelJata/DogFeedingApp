""" Main Flask Web App Module"""
import  math
# ,flash, redirect,  , session, abort
from flask import Flask, render_template, request
import json
from DataAccess import DataAccess

app = Flask(__name__)

@app.route("/")
def index():
    """This is the landing page"""
    page = request.args.get("page")
    if page is None:
        page = 0
    items_per_page = 5
    data_access = DataAccess()
    feed_history = data_access.get_feed_history_with_columns(page, items_per_page)
    amount_of_feed_entries = data_access.get_amount_of_feed_entries()
    feed_limit = data_access.get_feed_limit()
    food_served_today = data_access.get_total_foodserved_today()
    daily_feed_history = data_access.get_daily_feed_history()
    pages = math.ceil(amount_of_feed_entries[0] / items_per_page)
   
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
        page = 0
    items_per_page = 5
    feeder_name_input = request.form['feederNameInput']
    amount_of_food_input = request.form['amountOfFoodInput']
    data_access = DataAccess()
    add_food_result = data_access.add_feed_history(amount_of_food_input, feeder_name_input)
    feed_history = data_access.get_feed_history_with_columns(page, items_per_page)
    amount_of_feed_entries = data_access.get_amount_of_feed_entries()
    feed_limit = data_access.get_feed_limit()
    food_served_today = data_access.get_total_foodserved_today()
    daily_feed_history = data_access.get_daily_feed_history()
    pages = math.ceil(amount_of_feed_entries[0] / items_per_page)
    return render_template("dashboard.html", **locals())


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=666)
