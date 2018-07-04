class UserController:
    """Controller class for manipulating user data."""
    def __init__(self, user_dao):
        """
        Constructs a new UserController instance.
        :param user_dao: A dao.UserDAO instance.
        """
        self.user_dao = user_dao

    def get_user(self, user_id):
        """
        Gets a specific user by ID.
        :param user_id: The ID of the user to retrieve.
        :return: The user requested, or None if no user exists for that ID.
        """
        return self.user_dao.get_user(user_id)

    def add_user(self, user):
        """
        Adds a user to the service.
        :param user: A dict representing the user to add.
        """
        return self.user_dao.add_user(user)

    def update_user(self, user_id, **kwargs):
        """
        Updates a user in the service.
        :param user_id: The ID of the user to update.
        :param kwargs: Key-value pairs representing each attribute to update. If the attribute does not exist yet, it
                       will be created.
        """
        return self.user_dao.update_user(user_id, **kwargs)


class StopController:
    """Controller class for getting stop information."""
    def __init__(self, five_eleven_client):
        """
        Constructs a new StopController instance.
        :param five_eleven_client: A client.FiveElevenClient instance for making API calls.
        """
        self.five_eleven_client = five_eleven_client

    def get_upcoming_visits(self, agency, stop_id):
        """
        Gets upcoming visits to the specified stop. Usually this returns the next 3 arrivals at the stop, but the exact
        number of arrivals is not guaranteed.
        :param agency: The agency serviced by the stop (ex: 'SF').
        :param stop_id: The ID of the stop.
        :return: A list of dicts containing upcoming visits to the stop.
        """
        response = self.five_eleven_client.get_real_time_stop_monitoring(agency, stop_id)

        return response['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']


class LineController:
    def __init__(self, five_eleven_client):
        self.five_eleven_client = five_eleven_client

    def get_patterns_for_line(self, agency, line_id):
        response = self.five_eleven_client.get_patterns_for_line(agency, line_id)

        return response['journeyPatterns']


class SetupController:
    AGENCY = 'SF'

    def __init__(self, line_controller):
        self.line_controller = line_controller

    def get_stop_id(self, line_id, stop_name, direction):
        patterns = self.line_controller.get_patterns_for_line(self.AGENCY, line_id)

        for journey_pattern in patterns:
            if journey_pattern['DirectionRef'] == direction:

                stop_points = journey_pattern['PointsInSequence']['StopPointInJourneyPattern']
                for stop_point in stop_points:
                    if stop_point['Name'].lower() == stop_name:
                        return stop_point['ScheduledStopPointRef']

                timing_points = journey_pattern['PointsInSequence']['TimingPointInJourneyPattern']
                for timing_point in timing_points:
                    if timing_point['Name'].lower() == stop_name:
                        return timing_point['ScheduledStopPointRef']

        return None
