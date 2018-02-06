import sqlite3 as lite
import sys
 
con = lite.connect('DogFeedingDb.db')
 
with con:
    cur = con.cursor()    
    cur.execute("INSERT INTO FeedHistory (FoodServed, NameOfServer) VALUES(210,'Michael')")