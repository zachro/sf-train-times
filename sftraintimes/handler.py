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
    slots = event['request']['intent'].get('slots')
    dialog_state = event['request'].get('dialogState')
    response = {}

    try:
        if intent_name == 'SetHomeStopByIdIntent':
            home_stop_id = slots['stopId']['value']
            response = set_home_stop_id(user_id, home_stop_id, APP_CONFIG.get_user_controller())

        elif intent_name == 'SetHomeLineIntent':
            home_line = slots['line']['value']
            response = set_home_line(user_id, home_line, APP_CONFIG.get_user_controller())

        elif intent_name == 'SetHomeDirectionIntent':
            home_direction = slots['direction']['value']
            response = set_home_direction(user_id, home_direction, APP_CONFIG.get_user_controller())

        elif intent_name == 'SetHomeStopIntent':
            first_street = slots['firstStreet']['value']
            second_street = slots['secondStreet']['value']
            response = set_home_stop(user_id, first_street, second_street, APP_CONFIG.get_user_controller(),
                                     APP_CONFIG.get_setup_controller())

        elif intent_name == 'SetupDialogIntent':
            response = handle_setup_dialog(user_id, slots, dialog_state)

        elif intent_name == 'GetNextTrainIntent':
            response = get_next_train(user_id, APP_CONFIG.get_stop_controller(), APP_CONFIG.get_user_controller())

    except Exception as e:
        LOG.error(e)

    return response


def handle_setup_dialog(user_id, slots, dialog_state):
    response = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {}
    }

    if dialog_state == 'COMPLETED':
        response['response']['outputSpeech'] = {
            'type': 'PlainText',
            'text': 'All done.'
        }
    else:
        response['response']['directives'] = [
            {
                'type': 'Dialog.Delegate',
                'updatedIntent': {
                    'name': 'SetupDialogIntent',
                    'confirmationStatus': 'NONE',
                }
            }
        ]
        response['response']['shouldEndSession'] = False
        response['response']['directives'][0]['updatedIntent']['slots'] = slots

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
    """
    Handles a SetHomeLineIntent request.
    :param user_id: The ID of the device making the request.
    :param home_line: The name of the line (K, J, M, etc.)
    :param user_controller: A controller.UserController instance.
    :return: A dict containing the Alexa response.
    """
    user = user_controller.get_user(user_id)

    if user is None:
        user = {'id': user_id, 'homeLine': home_line}
        user_controller.add_user(user)
    else:
        user_controller.update_user(user_id, homeLine=home_line.upper())

    output_speech_text = 'I\'ve set your home line to {}.'.format(home_line)
    response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()

    return response


def set_home_direction(user_id, direction, user_controller):
    """
    Handles a SetHomeDirectionIntent request.
    :param user_id: The ID of the device making the request.
    :param direction: The direction: inbound or outbound.
    :param user_controller: A controller.UserController instance.
    :return: A dict containing the Alexa response.
    """
    direction_id = 'IB' if direction == 'inbound' else 'OB'

    user = user_controller.get_user(user_id)

    if user is None:
        user = {'id': user_id, 'direction': direction_id}
        user_controller.add_user(user)
    else:
        user_controller.update_user(user_id, direction=direction_id)

    output_speech_text = 'I\'ve set your home direction to {}.'.format(direction)
    response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()

    return response


def set_home_stop(user_id, first_street, second_street, user_controller, setup_controller):
    """
    Handles a SetHomeStopIntent request.
    :param user_id: The ID of the device making the request.
    :param first_street: The first cross street of the stop.
    :param second_street: The second cross street of the stop.
    :param user_controller: A controller.UserController instance.
    :param setup_controller: A controller.SetupController instance.
    :return: A dict containing the Alexa response.
    """
    first_st = _parse_street(first_street)
    second_st = _parse_street(second_street)
    user = user_controller.get_user(user_id)

    if user is None:
        output_speech_text = 'Sorry, you\'ll need to set your home line and direction before setting your home stop.'
        response = TrainTimesResponseBuilder().with_output_speech(output_speech_text)
        return response

    stop_id = setup_controller.get_stop_id(user['homeLine'], '{} & {}'.format(first_st, second_st), user['direction'])

    user_controller.update_user(user_id, homeStopId=stop_id)
    output_speech_text = 'I\'ve set your home stop to {} and {}'.format(first_street, second_street)
    response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()

    return response


def _parse_street(street):
    return street.replace('street', 'st')


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
        second_visit_diff = _get_wait_time(
            next_stops[1]['MonitoredVehicleJourney']['MonitoredCall']['AimedArrivalTime'])
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
