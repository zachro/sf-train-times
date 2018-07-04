import json
from botocore.vendored import requests


REAL_TIME_STOP_MONITORING_URL = 'http://api.511.org/transit/StopMonitoring'
LINE_PATTERN_URL = 'http://api.511.org/transit/patterns'


class FiveElevenClient:
    """Client for making calls to 511.org APIs."""
    def __init__(self, api_key):
        """Constructs a new FiveElevenClient instance."""
        self.api_key = api_key

    def get_real_time_stop_monitoring(self, agency, stop_id):
        """
        Gets upcoming arrivals for the given stop ID.
        :param agency: The agency serviced by this stop (ex: 'SF')
        :param stop_id: The ID of the stop.
        :return: A dict representing the API response.
        """
        query_params = {
            'api_key': self.api_key,
            'agency': agency,
            'stopCode': stop_id
        }
        response_object = requests.get(REAL_TIME_STOP_MONITORING_URL, params=query_params)
        if response_object.status_code != 200:
            raise RuntimeError('Response returned an unexpected status code. Response: {}'.format(response_object))

        response = self._parse_json(response_object.text)

        return response

    def get_patterns_for_line(self, agency, line_id):
        """
        Gets patterns for the specified line. A pattern represents the route a train travels on the line.
        :param agency: The agency serviced by this stop (ex: 'SF')
        :param line_id: The ID of the line (K, J, M, etc.)
        :return: A list of patterns serviced by this line.
        """
        query_params = {
            'api_key': self.api_key,
            'operator_id': agency,
            'line_id': line_id
        }
        response_object = requests.get(LINE_PATTERN_URL, params=query_params)
        if response_object.status_code != 200:
            raise RuntimeError('Response returned an unexpected status code. Response: {}'.format(response_object))

        response = self._parse_json(response_object.text)

        return response

    @staticmethod
    def _parse_json(serialized_json):
        if serialized_json[0] == '\ufeff':
            return json.loads(serialized_json[1:])
        return json.loads(serialized_json)
