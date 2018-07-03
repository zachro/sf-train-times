import config as config
import datetime
from util import TrainTimesResponseBuilder

APP_CONFIG = config.AppConfig()
NEXT_TRAIN_MESSAGE = 'The next train at your stop arrives in {} minutes.'
NEXT_TWO_TRAINS_MESSAGE = 'The next train at your stop arrives in {} minutes. After that, there\'s one in {} minutes.'


def handle_request(event, context):
    print('Received an event: {}'.format(event))

    user_id = event['session']['user']['userId']
    intent_name = event['request']['intent']['name']
    response = {}

    try:
        if intent_name == 'SetHomeStopIntent':
            home_stop_id = event['request']['intent']['slots']['stopId']['value']
            response = set_home_stop_id(user_id, home_stop_id, APP_CONFIG.get_user_controller())
        elif intent_name == 'GetNextTrainIntent':
            response = get_next_train(user_id, APP_CONFIG.get_stop_controller(), APP_CONFIG.get_user_controller())

    except Exception as e:
        print('ERROR: {}'.format(e))

    return response


def set_home_stop_id(user_id, home_stop_id, user_controller):
    user = user_controller.get_user(user_id)

    if user is None:
        user = {'id': user_id, 'homeStopId': home_stop_id}
        user_controller.add_user(user)
    else:
        user_controller.update_user(user_id, homeStopId=home_stop_id)

    output_speech_text = 'I\'ve set your home stop to {}'.format(home_stop_id)
    response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()

    return response


def get_next_train(user_id, stop_controller, user_controller):
    user = user_controller.get_user(user_id)
    if user is None:
        output_speech_text = 'Sorry, you\'ll need to set your home stop before asking for train times.'
        response = TrainTimesResponseBuilder().with_output_speech(output_speech_text)
        return response

    next_stops = stop_controller.get_upcoming_visits(user['provider'], user['homeStopId'])
    diff_min = get_wait_time(next_stops[0]['MonitoredVehicleJourney']['MonitoredCall']['AimedArrivalTime'])

    if diff_min < 5:
        second_visit_diff = get_wait_time(next_stops[1]['MonitoredVehicleJourney']['MonitoredCall']['AimedArrivalTime'])
        output_speech_text = NEXT_TWO_TRAINS_MESSAGE.format(diff_min, second_visit_diff)
        response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()
    else:
        output_speech_text = NEXT_TRAIN_MESSAGE.format(diff_min)
        response = TrainTimesResponseBuilder().with_output_speech(output_speech_text).build()

    return response


def get_wait_time(arrival_time):
    arrival = parse_datetime(arrival_time)
    diff = arrival - datetime.datetime.utcnow()

    return int(diff.total_seconds() // 60)


def parse_datetime(iso_date):
    year = int(iso_date[:4])
    month = int(iso_date[5:7])
    day = int(iso_date[8:10])
    hour = int(iso_date[11:13])
    minute = int(iso_date[14:16])
    second = int(iso_date[17:19])

    return datetime.datetime(year, month, day, hour, minute, second)
