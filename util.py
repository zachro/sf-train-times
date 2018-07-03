from datetime import datetime


class TrainTimesResponseBuilder:
    """Builder class for generating Alexa responses."""
    VERSION = '1.0'
    OUTPUT_SPEECH_TYPE = 'PlainText'
    CARD_TYPE = 'Simple'

    def __init__(self):
        """Constructs an instance of this builder."""
        self.output_speech_text = None
        self.card_title = None
        self.card_content = None

    def with_output_speech(self, output_speech_text):
        """Sets the response.outputSpeech field for the response to be generated."""
        self.output_speech_text = output_speech_text
        return self

    def with_card_title(self, card_title):
        """Sets the response.card.title field for the response to be generated."""
        self.card_title = card_title
        return self

    def with_card_content(self, card_content):
        """Sets the response.card.content field for the response to be generated."""
        self.card_content = card_content
        return self

    def build(self):
        """
        Builds the response dict.
        :return: A dict containing the outputSpeech and/or card provided to the builder, formatted as an Alexa response.
        """
        response = {'version': self.VERSION}

        if self.output_speech_text:
            response['response'] = {
                'outputSpeech': {
                    'type': self.OUTPUT_SPEECH_TYPE,
                    'text': self.output_speech_text
                }
            }

        if self._has_card():
            response['card'] = {
                'type': self.CARD_TYPE,
                'title': self.card_title,
                'content': self.card_content
            }

        return response

    def _has_card(self):
        return self.card_title and self.card_content


def parse_datetime(iso_date):
    year = int(iso_date[:4])
    month = int(iso_date[5:7])
    day = int(iso_date[8:10])
    hour = int(iso_date[11:13])
    minute = int(iso_date[14:16])
    second = int(iso_date[17:19])

    return datetime(year, month, day, hour, minute, second)
