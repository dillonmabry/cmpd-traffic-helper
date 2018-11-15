"""
Module for CMPD Traffic business logic
"""
from bs4 import BeautifulSoup

class CMPDService(object):
	"""
	Business logic service for manipulating/getting new data
	Args:
		database: the database to interact with
		soap_service: the soap interface to use
	"""
	def __init__(self, database, soap_service):
		self.database = database
		self.soap_service = soap_service

	def update_traffic_data(self, limit=500):
		"""
		Update the traffic data
		Args:
			limit: the limit of records to lookup via database
		"""
		# Get current events and event ids
		soap_res = self.soap_service.post()
		soup = BeautifulSoup(soap_res, 'lxml')
		current_accidents = soup.findAll('accidents')
		current_events = [item.get_text() for item in soup.findAll('event_no')]

		# Find old events from database that match current event ids
		old_events = []
		with self.database:
			cursor = self.database.collection.find({"event_no": { "$in": current_events }}, {"event_no":1}).limit(limit)
			for doc in cursor:
				if doc.get("event_no"):
					old_events.append(doc.get("event_no"))

		# Get differences and new accidents soup objects from diff ids
		diffs = set(current_events) - set(old_events)
		new_accidents = [item for item in current_accidents if any(diff in item.get_text() for diff in diffs)]

		# Cleanup bs4 tags convert to JSON to insert
		if new_accidents:
			clean_data = []
			for item in new_accidents:
                		json_obj = {}
                		for tag in item:
                        		json_obj[tag.name] = tag.get_text()
                		clean_data.append(json_obj)
			self.database.insert_bulk(clean_data)

