"""
Module for CMPD Traffic business logic
"""


class CMPDService(object):
    """
    Business logic service for manipulating/getting new data
    Args:
        database: the database to interact with
        rest_service: the rest service to use with api endpoint
        weather_service: the OpenWeatherAPI service
    """

    def __init__(self, database, rest_service, weather_service):
        self.database = database
        self.rest_service = rest_service
        self.weather_service = weather_service

    def update_traffic_data(self):
        """
        Update the traffic data persistence
        """
        # Get current events and event ids
        res = self.rest_service.get(
            params={'Content-Type': 'application/json'})
        res_data = res.json()
        current_accidents = res_data
        current_ids = [item.get('EventNo') for item in res_data]

        # Find existing events from persistence that match current event ids
        with self.database as db:
            exist_events = db.find_ids(
                collection="accidents", ids=current_ids, cursor_limit=500)

        # Get new accidents only
        diffs = set(current_ids) - set(exist_events)
        new_accidents = [item for item in current_accidents if any(
            diff in item.get('EventNo') for diff in diffs)]

        if new_accidents:
            final_data = []
            for json in new_accidents:
                weather_details = self.weather_service.get(
                    params={
                        'lat': json.get('Latitude'),
                        'lon': json.get('Longitude')
                    }
                )
                # Weather API data to dictionary
                json["weatherInfo"] = weather_details
                final_data.append(json)
            with self.database as db:
                db.insert_bulk(collection="accidentsv2",
                               items=final_data)  # persist data
