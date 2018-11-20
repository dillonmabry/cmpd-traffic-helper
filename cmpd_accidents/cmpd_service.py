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
        weather_service: the OpenWeatherAPI service
    """
    def __init__(self, database, soap_service, weather_service):
        self.database = database
        self.soap_service = soap_service
        self.weather_service = weather_service

    def find_events(self, event_ids, cursor_limit):
        """
        Return existing events from persistence
        Args:
            event_ids: event ids of current accident events
            cursor_limit: the number of records retrieved via cursor
        """
        exist_events = []
        with self.database:
            cursor = self.database.collection.find(
                {'event_no': {'$in': event_ids}}, {'event_no': 1}
                ).limit(cursor_limit)
            for doc in cursor:
                if doc.get('event_no'):
                    exist_events.append(doc.get('event_no'))
        return exist_events

    def update_traffic_data(self):
        """
        Update the traffic data persistence
        """
        # Get current events and event ids, parse via soup parser
        soap_res = self.soap_service.post()
        soup_service = SoupService(text=soap_res, parse_type='lxml')
        current_accidents = soup_service.findAll('accidents')
        current_ids = soup_service.get_text('event_no')

        # Find existing events from persistence that match current event ids
        exist_events = self.find_events(event_ids=current_ids, cursor_limit=500)

        # Get differences and new accidents soup objects from diff ids
        diffs = set(current_ids) - set(exist_events)
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