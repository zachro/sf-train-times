import json
import logging

import boto3

from sftraintimes.client import FiveElevenClient
from sftraintimes.controller import SetupController
from sftraintimes.dao import UserDAO
from sftraintimes.service import UserService, StopService, LineService

KEY_STORAGE_BUCKET = 'test-key-storage'
KEY_STORAGE_PATH = 'five_eleven_keys.json'


class AppConfig:
    """Wires up dependencies."""
    def __init__(self):
        """Constructs a new AppConfig instance."""
        self.dynamodb = boto3.resource('dynamodb')
        self.s3_client = boto3.client('s3')
        self.user_service = None
        self.stop_service = None
        self.setup_controller = None

    def get_user_service(self):
        """Returns a UserController instance."""
        if self.user_service is not None:
            return self.user_service

        user_table = self.dynamodb.Table('TrainUser-test')

        self.user_service = UserService(UserDAO(user_table))
        return self.user_service

    def get_stop_service(self):
        """Returns a StopController instance."""
        if self.stop_service is not None:
            return self.stop_service

        keys = self.s3_client.get_object(Bucket=KEY_STORAGE_BUCKET, Key=KEY_STORAGE_PATH)['Body'].read().decode('utf-8')
        api_key = json.loads(keys)['api_key']

        self.stop_service = StopService(FiveElevenClient(api_key))
        return self.stop_service

    def get_setup_controller(self):
        """Returns a SetupController instance."""
        if self.setup_controller is not None:
            return self.setup_controller

        keys = self.s3_client.get_object(Bucket=KEY_STORAGE_BUCKET, Key=KEY_STORAGE_PATH)['Body'].read().decode('utf-8')
        api_key = json.loads(keys)['api_key']

        line_service = LineService(FiveElevenClient(api_key))
        self.setup_controller = SetupController(line_service)
        return self.setup_controller

    @staticmethod
    def get_logger():
        logger = logging.getLogger('log')
        logger.setLevel(logging.WARNING)

        return logger
