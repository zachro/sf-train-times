class SetupController:
    """Controller class for setting user's home stop."""
    AGENCY = 'SF'

    def __init__(self, line_controller):
        """
        Constructs a new SetupController instance.
        :param line_controller: A controller.LineController instance for getting line patterns.
        """
        self.line_controller = line_controller

    def get_stop_id(self, line_id, stop_name, direction):
        """
        Gets a stop ID from a stop's human-readable name.
        :param line_id: The line the stop lies on.
        :param stop_name: The name of the stop (ex: 'church street and 16th street')
        :param direction: The direction of the specific stop (IB or OB)
        :return: The ID of the stop, or None if it cannot be found.
        """
        patterns = self.line_controller.get_patterns_for_line(self.AGENCY, line_id)

        for journey_pattern in patterns:
            if journey_pattern['DirectionRef'] == direction:

                stop_points = journey_pattern['PointsInSequence']['StopPointInJourneyPattern']
                for stop_point in stop_points:
                    if stop_point['Name'].lower() == stop_name:
                        return stop_point['ScheduledStopPointRef']

                timing_points = journey_pattern['PointsInSequence']['TimingPointInJourneyPattern']
                for timing_point in timing_points:
                    if timing_point['Name'].lower() == stop_name:
                        return timing_point['ScheduledStopPointRef']

        return None
