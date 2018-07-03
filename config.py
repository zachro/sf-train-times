import boto3
import dao as dao
import controller as service


class AppConfig:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.user_controller = None

    def get_user_service(self):
        if self.user_controller is not None:
            return self.user_controller

        user_table = self.dynamodb.Table('TrainUser-test')

        self.user_controller = service.UserController(dao.UserDAO(user_table))

        return self.user_controller
