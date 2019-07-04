## CMPD Traffic Helper (Traffic Analysis for Charlotte, NC)
[![Build Status](https://travis-ci.org/dillonmabry/cmpd-traffic-helper.svg?branch=master)](https://travis-ci.org/dillonmabry/cmpd-traffic-helper)
[![Python 3.4](https://img.shields.io/badge/python-3.4-blue.svg)](https://www.python.org/downloads/release/python-340/)
[![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/downloads/release/python-350/)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CMPD Traffic Alerts service for persistence data and also any predictions/model analysis. Updater service as well as traditional ML model utilities.

## Goals of Project
- Identify areas of improvement in Charlotte traffic flow
- Identify problems areas, specific roads needing attention
- Identify least likelihood route from point A to point B of having an accident
- Provide a web based area to allow suggested routing to minimize likelihood of an accident

APIs used:
- Charlotte Mecklenburg Near-real time accident feeds http://maps.cmpd.org/trafficaccidents/default.aspx
- OpenWeatherAPI weather location information https://openweathermap.org/api

Data used:
- CMPD Traffic Accidents (Accident information)
- NC-DOT ARC GIS (Road features)
- Charlotte Open Data Portal (Traffic volumes, population, traffic signals, spatial features)
- Live weather stats (OpenWeatherAPI)

## Install Instructions
This project has 2 Python projects **traffic_analyzer** and **cmpd_accidents**:
- cmpd_accidents is for persistence and storing accidents either as a callable script or through PyPI
- traffic_analyzer is for model creation/generation

Install locally:
```
pip install .
```
Install via PyPI:
```
pip install charlotte-traffic-analysis
```

## How to Use
Current usage:
1. Setup persistence for storing data (MongoDB or MySQL currently supported)
2. Setup database or collections as "accidents"
3. Setup OpenWeatherAPI account and API key
That's it! All other data is stored as reference data from the latest census information via Charlotte NC

To check for current accidents and store them in your persistence:
```
import cmpd_accidents as cmpd
cmpd.update_traffic_data(<MongoDB host>, <MongoDB port>, <OpenWeather api key>) 
```
or
```
python main.py <MongoDB host> <MongoDB port> <OpenWeather api key>
```
It is preferable to setup a job-type service to run the API incrementally over time.
Using cron via -nix type systems:
Clone the current repo:
```
git clone https://github.com/dillonmabry/cmpd-traffic-helper
```
Setup cron job to run every 5 minutes:
```
crontab -e
```
```
*/5 * * * * cd <your-repo-location>/cmpd_accidents && sudo python3 main.py mongodb://<user>:<password>@<host>/<databasename> <port> <OpenWeather api key>
```
## Note on Persistence
If you would rather use a relational persistence such as MySQL, the interface is already available for SQLAlchemy connect via the database module. Simply replace the "collection" argument with "table" for relational persistence. Seed scripts are available in resources/db feel free to replace with what table columns you prefer.

Persistence swap example:

Relational
```
from cmpd_accidents import SQLAlchemyConnect
db = SQLAlchemyConnect(connection_string='mysql+pymysql://<user>:<password>@<host>/<database>')
with self.database as db:
            exist_events = db.find_ids(table="accidents", ids=current_ids, cursor_limit=500)
with self.database as db:
                db.insert_bulk(table="accidents", items=final_data) # persist data
```
MongoDB
```
from cmpd_accidents import MongoDBConnect
db = MongoDBConnect(host='mongodb://<user>:<password>@<host>/<database>', port=27017)
with self.database as db:
            exist_events = db.find_ids(collection="accidents", ids=current_ids, cursor_limit=500)
with self.database as db:
                db.insert_bulk(collection="accidents", items=final_data) # persist data
```

## Tests
```
python setup.py test
```
## To-Do
- [X] Create API to use CMPD SOAP Service for latest traffic accident data
- [X] Setup generic persistence for use of different databases (MySQL, etc.)
- [X] Add integration tests
- [X] Setup Travis CI integration
- [X] Exploratory Data Analysis
- [X] Analyze existing traffic prediction models and develop mock model
- [ ] Test mock model and provide detailed transparency
- [ ] Utilize created model to provide insight for current traffic patterns and information
- [ ] Create Python web service via hosting solution to call mock model and integrate with web portal
- [ ] Finalize and push Python package to PyPI
- [ ] Fix any new bugs
- [ ] Create web based portal with interactivity

## Related R Notebook
This project was initially created via R and converted as best as possible to Python/Sklearn after decision to use Python to support model calling would be easier via web
