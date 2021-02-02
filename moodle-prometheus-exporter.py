from db_secrets import host
from db_secrets import user
from db_secrets import password
from db_secrets import database
from prometheus_client import start_http_server
from prometheus_client import Gauge
#from prometheus_client import Counter
#from prometheus_client import Histogram
#from prometheus_client import Info
import time
import mysql.connector


#timerange variables
intervall = 10 # sleep intervall - every 10 seconds a query is made by cursor

active_users = 0

#http server variables
server_port = 8899


# make sql connection
moodle_db = mysql.connector.connect(
  host = host,
  user = user,
  password = password,
  database = database

)


def get_metrics(moodle_db):

    #get and calc timestamps and generate query
    query_search_intervall = 300 # query intervall - 5min like in moodle
    timestamp_now=int(time.time())
    timestamp_start=(timestamp_now - query_search_intervall)

    DB_QUERY_ACTIVE_USER = "SELECT COUNT(*) FROM mdl_user WHERE deleted=0 AND lastaccess > {} AND lastaccess < {};".format(timestamp_start,timestamp_now)
    DB_QUERY_ONLINE_USER = "SELECT count(*) FROM mdl_user where timestampdiff(MINUTE, from_unixtime(lastaccess), now()) < 5;"
    DB_QUERY_ALL_USERS = "SELECT COUNT(*) FROM mdl_user WHERE deleted=0;"
    DB_QUERY_SIZE = "SELECT table_schema, SUM(data_length + index_length) / 1024 / 1024 AS 'DB Size in MB' FROM information_schema.tables WHERE table_schema = 'mz_moodle_db' GROUP BY table_schema;"

    #create cursor
    moodle_cursor = moodle_db.cursor()

    #should be a function...
    def get_active_users(moodle_cursor):
        moodle_cursor.execute(DB_QUERY_ACTIVE_USER)
        active_users = moodle_cursor.fetchone()  #returns array
        active_users = active_users[0]
        moodle_db.commit() #needed to commit the query and get new result on next query, otherwise result is always equal like first result
        return active_users

    def get_online_users(moodle_cursor):
        moodle_cursor.execute(DB_QUERY_ONLINE_USER)
        online_users = moodle_cursor.fetchone()  #returns array
        online_users = online_users[0]
        moodle_db.commit() #needed to commit the query and get new result on next query, otherwise result is always equal like first result
        return online_users

    def get_all_users(moodle_cursor):
        moodle_cursor.execute(DB_QUERY_ALL_USERS)
        all_users = moodle_cursor.fetchone()  #returns array
        all_users = all_users[0]
        moodle_db.commit() #needed to commit the query and get new result on next query, otherwise result is always equal like first result
        return all_users

    def get_db_size(moodle_cursor):
        moodle_cursor.execute(DB_QUERY_SIZE)
        db_size = moodle_cursor.fetchone()  #returns array
        db_size = db_size[1]
        moodle_db.commit() #needed to commit the query and get new result on next query, otherwise result is always equal like first result
        return db_size


    # run subfunctions
    active_users = get_active_users(moodle_cursor)
    online_users = get_online_users(moodle_cursor)
    all_users = get_all_users(moodle_cursor)
    db_size = get_db_size(moodle_cursor)
    moodle_cursor.close() # really needed to close it every loop step ?

    # print("Active Users: {}, Online Users: {}, All Users: {}, DB Size: {}".format(active_users,online_users,all_users,db_size))
    return active_users,online_users,all_users,db_size


# RUN
start_http_server(server_port)
gauge_active = Gauge('python_moodle_active_user_counter', 'This counter counts active users of last 5 minutes from moodle database')
gauge_online = Gauge('python_moodle_online_user_counter', 'This counter counts online users of last 5 minutes from moodle database')
gauge_all = Gauge('python_moodle_all_user_counter', 'This counter counts all users from moodle database')
gauge_db_size = Gauge('python_moodle_db_size_counter', 'This counter returns the size from moodle database')

try:
    while True:

        metrics = get_metrics(moodle_db)

        gauge_active.set(metrics[0])
        gauge_online.set(metrics[1])
        gauge_all.set(metrics[2])
        gauge_db_size.set(metrics[3])

        time.sleep(intervall)

except KeyboardInterrupt:
    moodle_cursor.close()
    moodle_db.close()
    print("Exiting...")
    exit(0)
