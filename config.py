import boto3
import dao
import client
import controller
import json

KEY_STORAGE_BUCKET = 'test-key-storage'
KEY_STORAGE_PATH = 'five_eleven_keys.json'


class AppConfig:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.s3_client = boto3.client('s3')
        self.user_controller = None
        self.stop_controller = None

    def get_user_controller(self):
        if self.user_controller is not None:
            return self.user_controller

        user_table = self.dynamodb.Table('TrainUser-test')

        self.user_controller = controller.UserController(dao.UserDAO(user_table))
        return self.user_controller

    def get_stop_controller(self):
        if self.stop_controller is not None:
            return self.stop_controller

        keys = self.s3_client.get_object(Bucket=KEY_STORAGE_BUCKET, Key=KEY_STORAGE_PATH)['Body'].read().decode('utf-8')
        api_key = json.loads(keys)['api_key']

        self.stop_controller = controller.StopController(client.FiveElevenClient(api_key))
        return self.stop_controller
