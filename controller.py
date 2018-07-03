class UserController:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def get_user(self, user_id):
        return self.user_dao.get_user(user_id)

    def add_user(self, user):
        return self.user_dao.add_user(user)

    def update_user(self, user_id, **kwargs):
        return self.user_dao.update_user(user_id, **kwargs)


class StopController:
    def __init__(self, five_eleven_client):
        self.five_eleven_client = five_eleven_client

    def get_upcoming_visits(self, agency, stop_id):
        response = self.five_eleven_client.real_time_stop_monitoring(agency, stop_id)

        return response['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']
