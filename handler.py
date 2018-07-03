import config as config


APP_CONFIG = config.AppConfig()


def handle_request(event, context):
    print('Received an event: {}'.format(event))

    user_id = event['session']['user']['userId']
    intent_name = event['request']['intent']['name']
    response = {}

    try:
        if intent_name == 'SetHomeCityIntent':
            home_city = event['request']['intent']['slots']['homeCity']['value']
            response = set_home_city(user_id, home_city, APP_CONFIG.get_user_controller())
        if intent_name == 'SetHomeStopIntent':
            response = set_home_stop_id(event, APP_CONFIG.get_user_controller())

    except Exception as e:
        print('ERROR: {}'.format(e))

    return response


def set_home_city(user_id, home_city, user_controller):
    user = user_controller.get_user(user_id)

    if user is None:
        user = {'id': user_id, 'homeCity': home_city}
        user_controller.add_user(user)
    else:
        user_controller.update_user(user_id, homeCity=home_city)

    response = {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': 'Successfully set your home city to {}'.format(home_city)
            }
        }
    }

    return response


def set_home_stop_id(event, user_controller):
    user_id = event['session']['user']['userId']
    home_stop_id = event['request']['intent']['slots']['stopId']['value']
    response = {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText'
            }
        }
    }

    user = user_controller.get_user(user_id)

    if user is None:
        response['response']['outputSpeech']['text'] = 'Please set your home city before setting your home stop.'
    else:
        user_controller.update_user(user_id, homeStopId=home_stop_id)
        response['response']['outputSpeech']['text'] = 'Successfully set your home stop to {}'.format(home_stop_id)

    return response
