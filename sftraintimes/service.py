from sftraintimes.client import FiveElevenClient
from sftraintimes.dao import UserDAO


AGENCY = 'SF'


class UserService:
    """Service class for manipulating user data."""
    def __init__(self, user_dao=UserDAO()):
        """
        Constructs a new UserService instance.
        :param user_dao: A UserDAO instance.
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
        :param kwargs: Key-value pairs representing each attribute to update. If the attribute does not exist, it will
                       be created.
        """
        return self.user_dao.update_user(user_id, **kwargs)


class StopService:
    """Service class for getting stop information."""
    def __init__(self, five_eleven_client=FiveElevenClient()):
        """
        Constructs a new StopService instance.
        :param five_eleven_client: A FiveElevenClient instance for making API calls.
        """
        self.five_eleven_client = five_eleven_client

    def get_upcoming_visits(self, stop_id):
        """
        Gets upcoming visits to the specified stop. Usually this returns the next 3 arrivals at the stop, but the exact
        number of arrivals is not guaranteed.
        :param stop_id: The ID of the stop.
        :return: A list of dicts containing upcoming visits to the stop.
        """
        response = self.five_eleven_client.get_real_time_stop_monitoring(AGENCY, stop_id)

        return response['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']


class LineService:
    """Service class for getting line information."""
    def __init__(self, five_eleven_client=FiveElevenClient()):
        """
        Constructs a new LineService instance.
        :param five_eleven_client: A FiveElevenClient instance for making API calls.
        """
        self.five_eleven_client = five_eleven_client

    def get_patterns_for_line(self, line_id):
        """
        Gets patterns for the specified line. Patterns represent possible routes a train for the given line could take.
        :param line_id: The ID of the line.
        :return: A list of patterns serviced by the line.
        """
        response = self.five_eleven_client.get_patterns_for_line(AGENCY, line_id)

        return response['journeyPatterns']
