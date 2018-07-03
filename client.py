import json
from botocore.vendored import requests


REAL_TIME_STOP_MONITORING_URL = 'http://api.511.org/transit/StopMonitoring'


class FiveElevenClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_real_time_stop_monitoring(self, agency, stop_id):
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

    @staticmethod
    def _parse_json(serialized_json):
        if serialized_json[0] == '\ufeff':
            return json.loads(serialized_json[1:])
        return json.loads(serialized_json)
