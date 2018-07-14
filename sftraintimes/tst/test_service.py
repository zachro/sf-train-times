from unittest import TestCase
from unittest.mock import Mock

from sftraintimes.client import FiveElevenClient
from sftraintimes.dao import UserDAO
from sftraintimes.service import UserService, StopService, LineService


class UserServiceTest(TestCase):
    USER_ID = 'userId'
    USER = {'id': 'userId'}

    def setUp(self):
        UserDAO.__init__ = Mock(return_value=None)
        self.mock_dao = UserDAO('table')
        self.user_service = UserService(self.mock_dao)

    def test_get_user(self):
        self.mock_dao.get_user = Mock(return_value=self.USER)

        result = self.user_service.get_user(self.USER_ID)

        self.assertEqual(result, self.USER)
        self.mock_dao.get_user.assert_called_with(self.USER_ID)

    def test_add_user(self):
        self.mock_dao.add_user = Mock()

        self.user_service.add_user(self.USER)

        self.mock_dao.add_user.assert_called_with(self.USER)

    def test_update_user(self):
        kwargs = {'firstAttribute': 'firstValue', 'secondAttribute': 'secondValue'}
        self.mock_dao.update_user = Mock()

        self.user_service.update_user(self.USER_ID, **kwargs)

        self.mock_dao.update_user.assert_called_with(self.USER_ID, **kwargs)


class StopServiceTest(TestCase):
    AGENCY = 'SF'
    STOP_ID = '12345'

    def setUp(self):
        FiveElevenClient.__init__ = Mock(return_value=None)
        self.mock_client = FiveElevenClient('foo')
        self.stop_service = StopService(self.mock_client)

    def test_get_upcoming_visits(self):
        self.mock_client.get_real_time_stop_monitoring = Mock(return_value=_get_stop_monitoring_response())
        expected = 'stopVisits'

        result = self.stop_service.get_upcoming_visits(self.STOP_ID)

        self.assertEqual(result, expected)
        self.mock_client.get_real_time_stop_monitoring.assert_called_with(self.AGENCY, self.STOP_ID)

    def test_get_upcoming_visits__no_visits(self):
        response_without_visits = _get_stop_monitoring_response()
        response_without_visits['ServiceDelivery']['StopMonitoringDelivery'].pop('MonitoredStopVisit')
        self.mock_client.get_real_time_stop_monitoring = Mock(return_value=response_without_visits)

        with self.assertRaises(KeyError):
            self.stop_service.get_upcoming_visits(self.STOP_ID)
        self.mock_client.get_real_time_stop_monitoring.assert_called_with(self.AGENCY, self.STOP_ID)


class LineServiceTest(TestCase):
    AGENCY = 'SF'
    LINE_ID = 'J'

    def setUp(self):
        FiveElevenClient.__init__ = Mock(return_value=None)
        self.mock_client = FiveElevenClient('foo')
        self.line_service = LineService(self.mock_client)

    def test_get_patterns_for_line(self):
        five_eleven_response = {'journeyPatterns': 'journeyPatternsList'}
        self.mock_client.get_patterns_for_line = Mock(return_value=five_eleven_response)
        expected = 'journeyPatternsList'

        result = self.line_service.get_patterns_for_line(self.LINE_ID)

        self.assertEqual(result, expected)
        self.mock_client.get_patterns_for_line.assert_called_with(self.AGENCY, self.LINE_ID)

    def test_get_patterns_for_line__no_patterns(self):
        five_eleven_response = {}
        self.mock_client.get_patterns_for_line = Mock(return_value=five_eleven_response)

        with self.assertRaises(KeyError):
            self.line_service.get_patterns_for_line(self.LINE_ID)
        self.mock_client.get_patterns_for_line.assert_called_with(self.AGENCY, self.LINE_ID)


def _get_stop_monitoring_response():
    return {
        'ServiceDelivery': {
            'StopMonitoringDelivery': {
                'MonitoredStopVisit': 'stopVisits'
            }
        }
    }
