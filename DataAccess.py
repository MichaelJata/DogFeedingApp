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
            with self.con:
                cur = self.con.cursor()
                cur.execute(
                    "INSERT INTO FeedHistory (FoodServed, NameOfServer) VALUES(?,?)", food_history_entry)
            return "success"

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

    def get_total_foodserved_today(self):
        """Returns the total amount of feed entries"""
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT SUM(FoodServed) from FeedHistory where Timestamp >= date('now', 'start of day')")
            total_amount_today = cur.fetchone()
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
