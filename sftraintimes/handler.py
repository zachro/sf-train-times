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
    LOG.warning('Received an event: {}'.format(event))

    user_id = event['session']['user']['userId']
    intent_name = event['request']['intent']['name']
    slots = event['request']['intent'].get('slots')
    dialog_state = event['request'].get('dialogState')

    try:
        if intent_name == 'SetHomeStopByIdIntent':
            response = handle_set_home_stop_by_id_intent(user_id, slots, UserService())

        elif intent_name == 'SetHomeStopIntent':
            response = handle_setup_dialog_intent(user_id, slots, dialog_state, UserService(), SetupController())

        elif intent_name == 'GetNextTrainIntent':
            response = handle_get_next_train_intent(user_id, StopService(), UserService())

        else:
            output_speech_text = 'Sorry, I don\'t think I can help with that.'
            response = ResponseBuilder(output_speech_text=output_speech_text).build()

    except Exception as e:
        LOG.error(e)
        output_speech_text = 'Sorry, something went wrong.'
        response = ResponseBuilder(output_speech_text=output_speech_text).build()

    return response


def handle_setup_dialog_intent(user_id, slots, dialog_state, user_service, setup_controller):
    response = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {}
    }

    if dialog_state == 'COMPLETED':
        line_id = slots['line']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
        # Temporary workaround for line change
        if line_id == 'J' or line_id == 'K':
            line_id = 'KJ'
        LOG.warning(slots)

        direction_heard = slots['direction']['resolutions']['resolutionsPerAuthority'][0].get('values')
        if direction_heard and direction_heard[0]['value']['name'] == 'OB':
            direction = 'OB'
        else:
            direction = 'IB'
        long_direction = 'inbound' if direction == 'IB' else 'outbound'
        first_street = slots['firstStreet']['value']
        second_street = slots['secondStreet']['value']
        first_st = parse_street(first_street)
        second_st = parse_street(second_street)
        stop_name = '{} & {}'.format(first_st, second_st)
        long_stop_name = '{} and {}'.format(first_street, second_street)

        home_stop_id = setup_controller.get_stop_id(line_id, stop_name, direction)
        user = user_service.get_user(user_id)
        if user is None:
            user = {'id': user_id, 'homeStopId': home_stop_id}
            user_service.add_user(user)
        else:
            user_service.update_user(user_id, homeStopId=home_stop_id)

        output_speech_text = 'I\'ve set your home stop to {} on the {} {} line'.format(long_stop_name, long_direction,
                                                                                       line_id)

        response = ResponseBuilder(output_speech_text=output_speech_text).build()
    else:
        response['response']['directives'] = [
            {
                'type': 'Dialog.Delegate',
                'updatedIntent': {
                    'name': 'SetHomeStopIntent',
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
