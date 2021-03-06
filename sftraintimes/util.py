from datetime import datetime


class ResponseBuilder:
    """Builder class for generating Alexa responses."""
    VERSION = '1.0'
    OUTPUT_SPEECH_TYPE = 'PlainText'
    CARD_TYPE = 'Simple'

    def __init__(self, output_speech_text=None):
        """Constructs an instance of this builder."""
        self.output_speech_text = output_speech_text

    def build(self):
        """
        Builds the response dict.
        :return: A dict containing the outputSpeech and/or card provided to the builder, formatted as an Alexa response.
        """
        response = {'version': self.VERSION, 'response': {}, 'sessionAttributes': {}}

        if self.output_speech_text:
            response['response']['outputSpeech'] = {
                'type': self.OUTPUT_SPEECH_TYPE,
                'text': self.output_speech_text
            }

        return response


def parse_datetime(iso_date):
    year = int(iso_date[:4])
    month = int(iso_date[5:7])
    day = int(iso_date[8:10])
    hour = int(iso_date[11:13])
    minute = int(iso_date[14:16])
    second = int(iso_date[17:19])

    return datetime(year, month, day, hour, minute, second)


def parse_street(literal_street):
    """
    Parses an AMAZON.StreetName slot from Alexa into a street name matching SFMTA formats. Example: 'market street' ->
    'market st', 'ocean avenue' -> 'ocean ave'
    :param literal_street: The street name as received from Alexa.
    :return: The street name formatted for matching against SFMTA stops.
    """
    if 'street' in literal_street:
        return literal_street.replace('street', 'st')
    if 'avenue' in literal_street:
        return literal_street.replace('avenue', 'ave')
    if 'boulevard' in literal_street:
        return literal_street.replace('boulevard', 'blvd')
    if 'drive' in literal_street:
        return literal_street.replace('drive', 'dr')
