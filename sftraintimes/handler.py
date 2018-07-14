import datetime

from sftraintimes.config import get_user_service, get_logger, get_setup_controller, get_stop_service
from sftraintimes.model import Direction
from sftraintimes.util import ResponseBuilder, parse_datetime, parse_street

LOG = get_logger()

NEXT_TRAIN_MESSAGE = 'The next train at your stop arrives in {} minutes.'
NEXT_TWO_TRAINS_MESSAGE = 'The next train at your stop arrives in {} minutes. After that, there\'s one in {} minutes.'
HELP_INTENT_MESSAGE = 'I can give you train arrival times for the stop closest to your Echo device. To start, ' \
                      'say, set my home stop. Once your home stop is set, you can find out when the next train ' \
                      'arrives at your stop by saying, get the next train from train times.'
FALLBACK_INTENT_MESSAGE = 'Sorry, I don\'t think I can help with that. Some things you can ask me are, get the next ' \
                          'train, or, set my home stop.'
LAUNCH_INTENT_MESSAGE = 'Welcome to train times. '


def handle_request(event, context):
    """
    Handles an incoming lambda event.
    :param event: The lambda event.
    :param context: The lambda context object.
    :return: An Alexa response object.
    """
    request = event['request']
    session = event['session']

    try:
        if request['type'] == 'LaunchRequest':
            return on_launch()
        elif request['type'] == 'IntentRequest':
            return on_intent(request, session)
        else:
            raise ValueError('Unrecognized request type: {}'.format(request))

    except Exception as e:
        LOG.exception(e)
        output_speech_text = 'Sorry, something went wrong.'
        response = ResponseBuilder(output_speech_text=output_speech_text).build()

    return response


def on_launch():
    """Handles a LaunchRequest from Alexa."""
    return handle_launch_request()


def on_intent(request, session):
    """
    Handles an IntentRequest from Alexa.
    :param request: The request object from the lambda event.
    :param session: The session object from the lambda event.
    :return: An Alexa response object.
    """
    intent_name = request['intent']['name']

    if intent_name == 'SetHomeStopByIdIntent':
        response = handle_set_home_stop_by_id_intent(request, session)
    elif intent_name == 'SetHomeStopIntent':
        response = handle_set_home_stop_intent(request, session)
    elif intent_name == 'GetNextTrainIntent':
        response = handle_get_next_train_intent(session)
    elif intent_name == 'AMAZON.HelpIntent':
        response = handle_help_intent()
    elif intent_name == 'AMAZON.FallbackIntent':
        response = handle_fallback_intent()
    else:
        LOG.warning('Unrecognized IntentRequest: {}'.format(request))
        response = handle_fallback_intent()

    return response


def handle_launch_request():
    """
    Handles a launch request.
    :return: A dict containing the Alexa response.
    """
    output_speech_text = LAUNCH_INTENT_MESSAGE + HELP_INTENT_MESSAGE
    return ResponseBuilder(output_speech_text=output_speech_text).build()


def handle_set_home_stop_intent(request, session, user_service=get_user_service(),
                                setup_controller=get_setup_controller()):
    """
    Handles a SetHomeStopIntent request.
    :param request: The Alexa request object.
    :param session: The Alexa session object.
    :param user_service: A UserService instance.
    :param setup_controller: A SetupController instance.
    :return: An Alexa response object.
    """
    dialog_state = request['dialogState']
    slots = request['intent']['slots']

    if dialog_state == 'COMPLETED':
        line_id = slots['line']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
        # Temporary workaround for KJ
        line_id = 'KJ' if line_id == 'J' or line_id == 'K' else line_id
        direction = Direction.from_string(
            slots['direction']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name'])
        first_street = slots['firstStreet']['value']
        second_street = slots['secondStreet']['value']
        first_st = parse_street(first_street)
        second_st = parse_street(second_street)
        stop_name = '{} & {}'.format(first_st, second_st)
        long_stop_name = '{} and {}'.format(first_street, second_street)

        home_stop_id = setup_controller.get_stop_id(line_id, stop_name, direction)

        user_id = session['user']['userId']
        user = user_service.get_user(user_id)

        if user is None:
            user = {'id': user_id, 'homeStopId': home_stop_id}
            user_service.add_user(user)
        else:
            user_service.update_user(user_id, homeStopId=home_stop_id)

        output_speech_text = 'I\'ve set your home stop to {} on the {} {} line'.format(long_stop_name,
                                                                                       direction.to_string(), line_id)

        response = ResponseBuilder(output_speech_text=output_speech_text).build()
    else:
        response = {
            'version': '1.0',
            'sessionAttributes': {},
            'response': {}
        }
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


def handle_set_home_stop_by_id_intent(request, session, user_service=get_user_service()):
    """
    Handles a SetHomeStopIntent request.
    :param request: The Alexa request object.
    :param session: The Alexa session object.
    :param user_service: A UserService instance.
    :return: An Alexa response object.
    """
    home_stop_id = request['intent']['slots']['stopId']['value']
    user_id = session['user']['userId']
    user = user_service.get_user(user_id)

    if user is None:
        user = {'id': user_id, 'homeStopId': home_stop_id}
        user_service.add_user(user)
    else:
        user_service.update_user(user_id, homeStopId=home_stop_id)

    output_speech_text = 'I\'ve set your home stop to {}.'.format(home_stop_id)
    response = ResponseBuilder(output_speech_text=output_speech_text).build()

    return response


def handle_get_next_train_intent(session, stop_service=get_stop_service(), user_service=get_user_service()):
    """
    Handles a GetNextTrainIntent request.
    :param session: The Alexa session object.
    :param stop_service: A StopController instance.
    :param user_service: A UserService instance.
    :return: An Alexa response object.
    """
    user_id = session['user']['userId']
    user = user_service.get_user(user_id)
    if user is None:
        output_speech_text = 'Sorry, you\'ll need to set your home stop before asking for train times.'
        response = ResponseBuilder(output_speech_text=output_speech_text).build()
        return response

    next_stops = stop_service.get_upcoming_visits(user['homeStopId'])
    diff_min = _get_wait_time(next_stops[0]['MonitoredVehicleJourney']['MonitoredCall']['AimedArrivalTime'])

    if diff_min < 5:
        next_visit_diff = _get_wait_time(next_stops[1]['MonitoredVehicleJourney']['MonitoredCall']['AimedArrivalTime'])
        output_speech_text = NEXT_TWO_TRAINS_MESSAGE.format(diff_min, next_visit_diff)
        response = ResponseBuilder(output_speech_text=output_speech_text).build()
    else:
        output_speech_text = NEXT_TRAIN_MESSAGE.format(diff_min)
        response = ResponseBuilder(output_speech_text=output_speech_text).build()

    return response


def handle_help_intent():
    """
    Handles the built-in AMAZON.HelpIntent.
    :return: An Alexa response object.
    """
    return ResponseBuilder(output_speech_text=HELP_INTENT_MESSAGE).build()


def handle_fallback_intent():
    """
    Handles the built-in AMAZON.FallbackIntent
    :return: An Alexa response object.
    """
    return ResponseBuilder(output_speech_text=FALLBACK_INTENT_MESSAGE).build()


def _get_wait_time(arrival_time):
    arrival = parse_datetime(arrival_time)
    diff = arrival - datetime.datetime.utcnow()

    return int(diff.total_seconds() // 60)
