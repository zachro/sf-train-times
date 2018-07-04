from sftraintimes import config as config
import datetime
from sftraintimes.util import TrainTimesResponseBuilder, parse_datetime

APP_CONFIG = config.AppConfig()
LOG = config.AppConfig.get_logger()

NEXT_TRAIN_MESSAGE = 'The next train at your stop arrives in {} minutes.'
NEXT_TWO_TRAINS_MESSAGE = 'The next train at your stop arrives in {} minutes. After that, there\'s one in {} minutes.'


def handle_request(event, context):
    """Handles an incoming request from Alexa."""
    LOG.debug('Received an event: {}'.format(event))

    user_id = event['session']['user']['userId']
    intent_name = event['request']['intent']['name']
    response = {}

    try:
        if intent_name == 'SetHomeStopByIdIntent':
            home_stop_id = event['request']['intent']['slots']['stopId']['value']
            response = set_home_stop_id(user_id, home_stop_id, APP_CONFIG.get_user_controller())
        elif intent_name == 'SetHomeLineIntent':
            home_line = event['request']['intent']['slots']['line']['value']
            response = set_home_line(user_id, home_line, APP_CONFIG.get_user_controller())
        elif intent_name == 'GetNextTrainIntent':
            response = get_next_train(user_id, APP_CONFIG.get_stop_controller(), APP_CONFIG.get_user_controller())

    except Exception as e:
        LOG.error(e)

    return response


def set_home_stop_id(user_id, home_stop_id, user_controller):
    """
    Handles a SetHomeStopIntent request.
    :param user_id: The ID of the device making the request.
    :param home_stop_id: The ID of the user's home stop.
    :param user_controller: A controller.UserController instance.
    :return: A dict containing the Alexa response.
    """
    user = user_controller.get_user(user_id)

    if user is None:
        user = {'id': user_id, 'homeStopId': home_stop_id}
        user_controller.add_user(user)
    else:
        user_controller.update_user(user_id, homeStopId=home_stop_id)

    output_speech_text = 'I\'ve set your home stop to {}.'.format(home_stop_id)
    response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()

    return response


def set_home_line(user_id, home_line, user_controller):
    user = user_controller.get_user(user_id)

    if user is None:
        user = {'id': user_id, 'homeLine': home_line}
        user_controller.add_user(user)
    else:
        user_controller.update_user(user_id, homeLine=home_line)

    output_speech_text = 'I\'ve set your home line to {}.'.format(home_line)
    response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()

    return response


def get_next_train(user_id, stop_controller, user_controller):
    """
    Handles a GetNextTrainIntent request.
    :param user_id: The ID of the device making the request.
    :param stop_controller: A controller.StopController instance for getting train information.
    :param user_controller: A controller.UserController instance.
    :return: A dict containing the Alexa response.
    """
    user = user_controller.get_user(user_id)
    if user is None:
        output_speech_text = 'Sorry, you\'ll need to set your home stop before asking for train times.'
        response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()
        return response

    next_stops = stop_controller.get_upcoming_visits(user['provider'], user['homeStopId'])
    diff_min = _get_wait_time(next_stops[0]['MonitoredVehicleJourney']['MonitoredCall']['AimedArrivalTime'])

    if diff_min < 5:
        second_visit_diff = _get_wait_time(next_stops[1]['MonitoredVehicleJourney']['MonitoredCall']['AimedArrivalTime'])
        output_speech_text = NEXT_TWO_TRAINS_MESSAGE.format(diff_min, second_visit_diff)
        response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()
    else:
        output_speech_text = NEXT_TRAIN_MESSAGE.format(diff_min)
        response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()

    return response


def _get_wait_time(arrival_time):
    arrival = parse_datetime(arrival_time)
    diff = arrival - datetime.datetime.utcnow()

    return int(diff.total_seconds() // 60)
