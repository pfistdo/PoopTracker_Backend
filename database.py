import socket
import json
import mysql.connector
from mysql.connector import errorcode

def get_mysql_connection():
    # Determine the environment (local or pythonanywhere)
    config_file_path = "config.json"
    if "PC24" in socket.gethostname():
        environment = "local"
        # config_file_path = "config.json"
    else:
        environment = "amazon"
        # config_file_path = "/home/pfistdo/mysite/config.json"

    # Load the configuration from the JSON file
    with open(config_file_path) as config_file:
        db_config = json.load(config_file)


    try:
        cnx = mysql.connector.connect(
            user=db_config.get(environment).get("user"),
            password=db_config.get(environment).get("password"),
            host=db_config.get(environment).get("host"),
            database=db_config.get(environment).get("database")
        )
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None
