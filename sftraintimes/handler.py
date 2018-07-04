import datetime

import sftraintimes.config as config
from sftraintimes.controller import SetupController
from sftraintimes.service import UserService, StopService
from sftraintimes.util import ResponseBuilder, parse_datetime, parse_street

LOG = config.get_logger()

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
            response = handle_set_home_stop_by_id_intent(user_id, slots, UserService())

        elif intent_name == 'SetHomeLineIntent':
            response = handle_set_home_line_intent(user_id, slots, UserService())

        elif intent_name == 'SetHomeDirectionIntent':
            response = handle_set_home_direction_intent(user_id, slots, UserService())

        elif intent_name == 'SetHomeStopIntent':
            response = handle_set_home_stop_intent(user_id, slots, UserService(), SetupController())

        elif intent_name == 'SetupDialogIntent':
            response = handle_setup_dialog_intent(user_id, slots, dialog_state)

        elif intent_name == 'GetNextTrainIntent':
            response = handle_get_next_train_intent(user_id, StopService(), UserService())

    except Exception as e:
        LOG.error(e)

    return response


def handle_setup_dialog_intent(user_id, slots, dialog_state):
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


def handle_set_home_stop_by_id_intent(user_id, slots, user_service):
    """
    Handles a SetHomeStopIntent request.
    :param user_id: The ID of the device making the request.
    :param slots: The slots contained in the IntentRequest.
    :param user_service: A UserService instance.
    :return: A dict containing the Alexa response.
    """
    home_stop_id = slots['stopId']['value']
    user = user_service.get_user(user_id)

    if user is None:
        user = {'id': user_id, 'homeStopId': home_stop_id}
        user_service.add_user(user)
    else:
        user_service.update_user(user_id, homeStopId=home_stop_id)

    output_speech_text = 'I\'ve set your home stop to {}.'.format(home_stop_id)
    response = ResponseBuilder(output_speech_text=output_speech_text).build()

    return response


def handle_set_home_line_intent(user_id, slots, user_service):
    """
    Handles a SetHomeLineIntent request.
    :param user_id: The ID of the device making the request.
    :param slots: The slots contained in the IntentRequest.
    :param user_service: A UserService instance.
    :return: A dict containing the Alexa response.
    """
    home_line = slots['line']['value']
    user = user_service.get_user(user_id)

    if user is None:
        user = {'id': user_id, 'homeLine': home_line}
        user_service.add_user(user)
    else:
        user_service.update_user(user_id, homeLine=home_line.upper())

    output_speech_text = 'I\'ve set your home line to {}.'.format(home_line)
    response = ResponseBuilder(output_speech_text=output_speech_text).build()

    return response


def handle_set_home_direction_intent(user_id, slots, user_service):
    """
    Handles a SetHomeDirectionIntent request.
    :param user_id: The ID of the device making the request.
    :param slots: The slots contained in the IntentRequest.
    :param user_service: A UserService instance.
    :return: A dict containing the Alexa response.
    """
    direction = slots['direction']['value']
    direction_id = 'IB' if direction == 'inbound' else 'OB'

    user = user_service.get_user(user_id)

    if user is None:
        user = {'id': user_id, 'direction': direction_id}
        user_service.add_user(user)
    else:
        user_service.update_user(user_id, direction=direction_id)

    output_speech_text = 'I\'ve set your home direction to {}.'.format(direction)
    response = ResponseBuilder(output_speech_text=output_speech_text).build()

    return response


def handle_set_home_stop_intent(user_id, slots, user_service, setup_controller):
    """
    Handles a SetHomeStopIntent request.
    :param user_id: The ID of the device making the request.
    :param slots: The slots contained in the IntentRequest.
    :param user_service: A UserService instance.
    :param setup_controller: A controller.SetupController instance.
    :return: A dict containing the Alexa response.
    """
    first_street = slots['firstStreet']['value']
    second_street = slots['secondStreet']['value']
    first_st = parse_street(first_street)
    second_st = parse_street(second_street)
    user = user_service.get_user(user_id)

    if user is None:
        output_speech_text = 'Sorry, you\'ll need to set your home line and direction before setting your home stop.'
        response = ResponseBuilder(output_speech_text=output_speech_text).build()
        return response

    stop_id = setup_controller.get_stop_id(user['homeLine'], '{} & {}'.format(first_st, second_st), user['direction'])

    user_service.update_user(user_id, homeStopId=stop_id)
    output_speech_text = 'I\'ve set your home stop to {} and {}'.format(first_street, second_street)
    response = ResponseBuilder(output_speech_text=output_speech_text).build()

    return response


def handle_get_next_train_intent(user_id, stop_controller, user_service):
    """
    Handles a GetNextTrainIntent request.
    :param user_id: The ID of the device making the request.
    :param stop_controller: A controller.StopController instance for getting train information.
    :param user_service: A UserService instance.
    :return: A dict containing the Alexa response.
    """
    user = user_service.get_user(user_id)
    if user is None:
        output_speech_text = 'Sorry, you\'ll need to set your home stop before asking for train times.'
        response = ResponseBuilder(output_speech_text=output_speech_text).build()
        return response

    next_stops = stop_controller.get_upcoming_visits(user['homeStopId'])
    diff_min = _get_wait_time(next_stops[0]['MonitoredVehicleJourney']['MonitoredCall']['AimedArrivalTime'])

    if diff_min < 5:
        next_visit_diff = _get_wait_time(next_stops[1]['MonitoredVehicleJourney']['MonitoredCall']['AimedArrivalTime'])
        output_speech_text = NEXT_TWO_TRAINS_MESSAGE.format(diff_min, next_visit_diff)
        response = ResponseBuilder(output_speech_text=output_speech_text).build()
    else:
        output_speech_text = NEXT_TRAIN_MESSAGE.format(diff_min)
        response = ResponseBuilder(output_speech_text=output_speech_text).build()

    return response


def _get_wait_time(arrival_time):
    arrival = parse_datetime(arrival_time)
    diff = arrival - datetime.datetime.utcnow()

    return int(diff.total_seconds() // 60)
