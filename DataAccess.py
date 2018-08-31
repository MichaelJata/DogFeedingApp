import sqlite3 as lite
import sys
import json


class DataAccess(object):
    def __init__(self, *args, **kwargs):
        self.con = lite.connect('DogFeedingDb.db')

    def add_feed_history(self, food_amount, server_name):
        """Adds food to the history"""
        if(food_amount == "" or server_name == ""):
            return "No values for food and server provided!"
        else:
            food_history_entry = (food_amount, server_name)
            food_served_today = int(self.get_total_food_served_today())
            feed_limit = int(self.get_feed_limit())
            if(int(food_amount) + food_served_today > feed_limit):
                return "You are exceeding the daily feed limit for Guinness! Reduce you generosity"
            with self.con:
                cur = self.con.cursor()
                cur.execute(
                    "INSERT INTO FeedHistory (FoodServed, NameOfServer) VALUES(?,?)", food_history_entry)
            return "success"
            
    def set_fill_level(self, fill_level_percentage):
        """Adds food to the history"""
        with self.con:
            cur = self.con.cursor()
            cur.execute(
                "update DeviceInfo set FillLevel = ?", (fill_level_percentage,))
        return "success"
    
    def set_operation_status(self, boolean_inOperation):
        """Sets the operation status of the dispenser in the db"""
        with self.con:
            cur = self.con.cursor()
            cur.execute(
                "update DeviceInfo set InOperation = ?", (boolean_inOperation,))
        return "success"

    def get_device_info(self):
        """Returns the total amount of feed entries"""
        with self.con:
            cur = self.con.cursor()
            cur.execute("Select * From DeviceInfo")
            device_info = cur.fetchone()
            return device_info

    def get_feed_history_with_columns(self, page, count):
        """Returns food which has been feeded in the past"""
        with self.con:
            pagination = (page, count)
            self.con.row_factory = lite.Row
            cur = self.con.cursor()
            cur.execute(
                "SELECT * FROM  FeedHistory ORDER BY Timestamp DESC LIMIT ?,?", pagination)
            rows = cur.fetchall()
            return rows
            """SELECT * FROM  FeedHistory ORDER BY Timestamp DESC LIMIT 0,5"""

    def get_amount_of_feed_entries(self):
        """Returns the total amount of feed entries"""
        with self.con:
            cur = self.con.cursor()
            cur.execute("Select COUNT(*) from FeedHistory")
            total_amount = cur.fetchone()
            return total_amount

    def get_daily_feed_history(self):
        """Returns the total amount of feed entries"""
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT SUM(FoodServed) as Amount, strftime('%d.%m.%Y', Timestamp) as Day from FeedHistory group by strftime('%d', Timestamp) order by Timestamp ASC limit 30")
            rows = cur.fetchall()
            total_amount_per_day = []
            for row in rows:
                total_amount_per_day.append(list(row))

            jsonResult = json.dumps(total_amount_per_day)
            return jsonResult

    def get_total_food_served_today(self):
        """Returns the total amount of feed entries"""
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT SUM(FoodServed) from FeedHistory where Timestamp >= date('now', 'start of day')")
            total_amount_today = cur.fetchone()
            if(total_amount_today[0] is None):
                return 0
            else:
                return total_amount_today[0]

    def get_feed_limit(self):
        """Returns the default feed limit per day"""
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT FoodLimitPerDay FROM LIMITS WHERE ID=1")
            food_limit = cur.fetchone()
            return food_limit[0]

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
