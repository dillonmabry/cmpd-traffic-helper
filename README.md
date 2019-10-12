## CMPD Traffic Helper (Traffic Analysis for Charlotte, NC)
[![Build Status](https://travis-ci.org/dillonmabry/cmpd-traffic-helper.svg?branch=master)](https://travis-ci.org/dillonmabry/cmpd-traffic-helper)
[![Python 3.4](https://img.shields.io/badge/python-3.4-blue.svg)](https://www.python.org/downloads/release/python-340/)
[![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/downloads/release/python-350/)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CMPD Traffic Alerts service for persistence data and also any predictions/model analysis. Updater service as well as traditional ML model utilities.

## Goals of Project
- Data collection of all reported traffic incidents in Charlotte
- Identify areas of improvement in Charlotte traffic flow
- Identify problems areas, specific roads needing attention
- Identify least likelihood route from point A to point B of having an accident

Data/APIs used:
- Charlotte Mecklenburg Near-real time accident feeds http://maps.cmpd.org/trafficaccidents/default.aspx
- OpenWeatherAPI weather location information https://openweathermap.org/api
- Charlotte Open Data Portal http://data.charlottenc.gov/

## Install Instructions
This repo has multiple projects:
- *cmpd_accidents* is for persistence and storing accidents as a command-line tool
- *traffic_analyzer* is for model creation/generation/testing as a command-line tool
- *cloud_predict* contains samples for interacting with existing cloud models via Google Cloud AI Platform
- *traffic_analyzer_api* is an API gateway for hosting a local API for development purposes

Install locally:
```
pip install .
```
Install via PyPI:
```
pip install charlotte-traffic-analysis
```

## Setup
Current usage:
1. Setup persistence for storing data (MongoDB or MySQL currently supported)
2. Setup database table or collections as ```accidents```
3. Setup OpenWeatherAPI account and API key
4. Run any command line tools using your persistence connection and weather API key

That's it! All other data is stored as reference data from the latest census information via Charlotte NC. To update reference data, download from the Charlotte Data Portal and update your install locally if needed.

To check for current accidents and store them via MongoDB:
```
import cmpd_accidents as cmpd
cmpd.update_traffic_data(<MongoDB host>, <MongoDB port>, <OpenWeather api key>) 
```
It is preferable to setup a job-type service to run the API incrementally over time.
Setup cron job to run every 5 minutes:
```
*/5 * * * * cd <your-repo-location>/cmpd_accidents && sudo python3 main.py mongodb://<user>:<password>@<host>/<databasename> <port> <OpenWeather api key>
```

## Note on Persistence
If you would rather use a relational persistence such as MySQL, the interface is already available for SQLAlchemy connect via the database module. Simply replace the "collection" argument with "table" for relational persistence. Seed scripts are available in resources/db feel free to replace with what table columns you prefer.

Persistence swap example:
```
from cmpd_accidents import SQLAlchemyConnect
db = SQLAlchemyConnect(connection_string='mysql+pymysql://<user>:<password>@<host>/<database>')
with self.database as db:
            exist_events = db.find_ids(table="accidents", ids=current_ids, cursor_limit=500)
with self.database as db:
                db.insert_bulk(table="accidents", items=final_data) # persist data
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
- [ ] Test mock models and provide detailed transparency
- [ ] Utilize created model to provide insight for current traffic patterns and information
- [ ] Create Python web service via hosting solution to call mock model and integrate with web portal
- [ ] Finalize and push Python package to PyPI
- [ ] Fix any new bugs
- [ ] Create web based portal with interactivity
