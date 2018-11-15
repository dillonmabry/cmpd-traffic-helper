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

	def update_traffic_data(self, limit=100):
		"""
		Update the traffic data
		Args:
			limit: the limit of records to lookup via database
		"""
		soap_res = self.soap_service.post()
		soup = BeautifulSoup(soap_res, 'lxml')
		current_accidents = soup.findAll('accidents')
		current_events = [item.get_text() for item in soup.findAll('event_no')]

		# Find differences
		with self.database:
			cursor = self.database.collection.find({"EVENT_NO": { "$in": current_events }}, {"EVENT_NO":1}).limit(limit)
			old_events = []
			for doc in cursor:
				if doc.get("EVENT_NO"):
					old_events.append(doc.get("EVENT_NO"))

		# Get differences and new accidents
		diffs = set(old_events).symmetric_difference(set(current_events))
		new_accidents = [item for item in current_accidents if any(diff in item.get_text() for diff in diffs)]

		# Cleanup bs4 tags convert to JSON
		if new_accidents:
			clean_data = []
			for item in new_accidents:
                		json_obj = {}
                		for tag in item:
                        		json_obj[tag.name] = tag.get_text()
                		clean_data.append(json_obj)
			self.database.insert_bulk(clean_data)

