# PoopTracker Backend

Backend server to handle all requests for the PoopTracker project in ZHAW course IoT- Data Streaming & Analytics. The server manages insert and select SQL statements sent from the Raspberry Pi and from the PoopTracker Dashboard application.


## Project structure

The backend server can be executed by running the [main.py](main.py) module. The database connection is handled by the [db_connector.py](database/db_connector.py) module located in the database folder. This folder also contains the SQL create statements to create the whole database. The database connection information is saved in [config.json](config/config.json). This file differentiates between a local and productive installation.
All endpoints that can be accessed by the Rasperry Pi or PoopTracker Dashboard are located in the [endpoints](endpoints) folder. The entities are stored inside the folder [models](models). To create a websocket connection between the backend server and the PoopTracker Dashboard the module [websocket_manager.py](websocket_manager.py) located in the root folder is used.
```
PoopTracker_Backend/
┣ config/
┃ ┗ config.json
┣ database/
┃ ┣ create_db.sql
┃ ┗ db_connector.py
┣ docs/
┃ ┗ ERD.png
┣ endpoints/
┃ ┣ air_qualities.py
┃ ┣ cats.py
┃ ┣ feedings.py
┃ ┣ foods.py
┃ ┣ poops.py
┃ ┣ telephone_numbers.py
┃ ┗ weights.py
┣ models/
┃ ┣ air_quality.py
┃ ┣ cat.py
┃ ┣ feeding.py
┃ ┣ food.py
┃ ┣ poop.py
┃ ┣ telephone_number.py
┃ ┗ weight.py
┣ .gitignore
┣ main.py
┣ Procfile
┣ README.md
┣ requirements.txt
┗ websocket_manager.py
```

## Database schema

![DB schema](https://i.imgur.com/HDjNKpX.png)

## Local installation

The project can be installed locally by completing the following checklist.

1. Clone the repository: `git clone https://github.com/pfistdo/PoopTracker_Backend.git`
2. Create a new venv: `python -m venv venv`
3. Activate the venv: `.\venv\Scripts\activate`
4. Install all dependencies: `pip install -r requirements.txt`
5. Create the database by using the SQL create statements located in [create_db.sql](database/create_db.sql)
6. Adjust the [config.json](config/config.json) to match your configuration.
7. Start the server by executing [main.py](main.py)

## API Reference

The backend server provides a Swagger API documentation that can be found on https://poop-tracker-48b06530794b.herokuapp.com/docs or locally on http://localhost:8000/docs. 

## Authors

- [@pfistdo](https://github.com/pfistdo)
