"""
Module for CMPD Traffic business logic
"""
from cmpd_accidents import SoupService

class CMPDService(object):
    """
    Business logic service for manipulating/getting new data
    Args:
        database: the database to interact with
        soap_service: the soap interface to use
    """
    def __init__(self, database, soap_service, weather_service):
        self.database = database
        self.soap_service = soap_service
        self.weather_service = weather_service

    def update_traffic_data(self, limit=500):
        """
        Update the traffic data
        Args:
            limit: the limit of records to lookup via database
        """
        # Get current events and event ids, parse via soup parser
        soap_res = self.soap_service.post()
        soup_service = SoupService(text=soap_res, parse_type='lxml')
        current_accidents = soup_service.findAll('accidents')
        current_events = soup_service.get_text('event_no')

        # Find old events from database that match current event ids
        old_events = []
        with self.database:
            cursor = self.database.collection.find({'event_no': {'$in': current_events}}, {'event_no': 1}).limit(limit)
            for doc in cursor:
                if doc.get('event_no'):
                    old_events.append(doc.get('event_no'))

        # Get differences and new accidents soup objects from diff ids
        diffs = set(current_events) - set(old_events)
        new_accidents = [item for item in current_accidents if any(diff in item.get_text() for diff in diffs)]

        # Cleanup bs4 tags convert to JSON to insert for cleaned data
        if new_accidents:
            json_data = soup_service.get_json(new_accidents)
            # Add weather API data for new accidents identified for each json object
            final_data = []
            for json in json_data:
                weather_details = self.weather_service.get(
                    params={'lat': json.get('latitude'), 'lon': json.get('longitude')}
                    )
                json["weatherInfo"] = weather_details
                final_data.append(json)
            self.database.insert_bulk(final_data) # persist data