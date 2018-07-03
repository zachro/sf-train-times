class TrainTimesResponseBuilder:
    VERSION = '1.0'
    OUTPUT_SPEECH_TYPE = 'PlainText'
    CARD_TYPE = 'Simple'

    def __init__(self):
        self.output_speech_text = None
        self.card_title = None
        self.card_content = None

    def with_output_speech(self, output_speech_text):
        self.output_speech_text = output_speech_text
        return self

    def with_card_title(self, card_title):
        self.card_title = card_title
        return self

    def with_card_content(self, card_content):
        self.card_content = card_content
        return self

    def build(self):
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
