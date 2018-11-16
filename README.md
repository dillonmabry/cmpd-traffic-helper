## CMPD Traffic Helper (Live Traffic Analysis for Charlotte, NC)
CMPD Traffic Alerts service for persistence data and also any predictions/model analysis. Updater service as well as traditional ML model utilities.

## Install Instructions
```
pip install .
```
TODO* Push to PyPI/setup Travis CI once pre-release stable build finished

## How to Use
Current usage:
```
import cmpd_accidents as cmpd
cmpd.update_traffic_data(<MongoDB host>, <MongoDB port>, <MongoDB collection>) 
```
or
```
python main.py <MongoDB host> <MongoDB port> <MongoDB collection>
```

## Tests
```
python setup.py test
```
## To-Do
- [X] Create API to use CMPD SOAP Service for latest traffic accident data
- [ ] Setup generic persistence for use of different databases (MySQL, etc.)
- [ ] Setup Travis CI and push to PyPI for pre-release helper service
- [ ] Create initial Python package
- [ ] Analyze existing traffic prediction models and develop mock model
- [ ] Utilize created model to provide insight for updated/real time traffic analysis
- [ ] Finalize Python package for project
- [ ] Fix any new bugs
- [ ] Create web based portal
