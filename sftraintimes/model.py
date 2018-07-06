from enum import Enum


class Direction(Enum):
    INBOUND = 'IB'
    OUTBOUND = 'OB'

    def to_string(self):
        return self.name.lower()

    @staticmethod
    def from_string(string):
        if string == 'IB':
            return Direction.INBOUND
        if string == 'OB':
            return Direction.OUTBOUND
        raise ValueError('String {} does not match values for Direction.'.format(string))
