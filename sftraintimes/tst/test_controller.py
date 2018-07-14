from unittest import TestCase
from unittest.mock import Mock

from sftraintimes.client import FiveElevenClient
from sftraintimes.controller import SetupController
from sftraintimes.model import Direction


class SetupControllerTest(TestCase):
    LINE_ID = 'J'
    STOP_NAME = 'church st & 24th st'
    DIRECTION = Direction.INBOUND

    def setUp(self):
        FiveElevenClient.__init__ = Mock(return_value=None)
        self.mock_client = FiveElevenClient('foo')
        self.setup_controller = SetupController(self.mock_client)

    def test_get_stop_id(self):
        self.mock_client.get_patterns_for_line = Mock(return_value=self._get_line_patterns())
        expected = '13996'

        result = self.setup_controller.get_stop_id(self.LINE_ID, self.STOP_NAME, self.DIRECTION)

        self.assertEqual(result, expected)
        self.mock_client.get_patterns_for_line.assert_called_with(self.LINE_ID)

    def test_get_stop_id__empty_api_response(self):
        empty_response = [{'DirectionRef': 'IB', 'PointsInSequence': {'StopPointInJourneyPattern': [],
                                                                      'TimingPointInJourneyPattern': []}}]
        self.mock_client.get_patterns_for_line = Mock(return_value=empty_response)

        result = self.setup_controller.get_stop_id(self.LINE_ID, self.STOP_NAME, self.DIRECTION)

        self.assertIsNone(result)
        self.mock_client.get_patterns_for_line.assert_called_with(self.LINE_ID)

    @staticmethod
    def _get_line_patterns():
        return [
            {
                'DirectionRef': 'IB',
                'PointsInSequence': {
                    'StopPointInJourneyPattern': [
                        {
                            'Name': 'Church St & 18th St',
                            'ScheduledStopPointRef': '13895'
                        }
                    ],
                    'TimingPointInJourneyPattern': [
                        {
                            'Name': 'Church St & 24th St',
                            'ScheduledStopPointRef': '13996'
                        }
                    ]
                }
            }
        ]
