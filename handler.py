import config as config


APP_CONFIG = config.AppConfig()


def set_home_city(event, context):
    return set_home_city_impl(event, APP_CONFIG.get_user_service())


def set_home_city_impl(event, user_controller):
    print('Received an event! {}'.format(event))

    user_id = event['session']['user']['userId']
    home_city = event['request']['intent']['slots']['homeCity']['value']

    try:
        user = user_controller.get_user(user_id)

        if user is None:
            user = {'id': user_id, 'homeCity': home_city}
            user_controller.add_user(user)
        else:
            user_controller.update_user(user_id, 'homeCity', home_city)

    except Exception as e:
        print('ERROR: {}'.format(e))

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
