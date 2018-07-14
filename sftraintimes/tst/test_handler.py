from unittest import TestCase
from unittest.mock import Mock, patch

from sftraintimes.handler import handle_request, on_launch, on_intent, handle_help_intent, handle_fallback_intent, \
    handle_launch_request, handle_set_home_stop_by_id_intent, handle_set_home_stop_intent, handle_get_next_train_intent


class HandlerTest(TestCase):
    def setUp(self):
        pass


def _get_sample_request(request_type):
    if request_type == 'LaunchRequest':
        request = {
            'type': 'LaunchRequest'
        }
    elif request_type == 'IntentRequest':
        request = {
            'type': 'IntentRequest',
            'intent': {}
        }
    else:
        raise ValueError('Invalid request type: {}'.format(request_type))

